from Database.db import get_connection


def _build_payment(conn, payment_id: int) -> dict:
    row = conn.execute(
        "SELECT * FROM payments WHERE payment_id = ?", (payment_id,)
    ).fetchone()
    if not row:
        return None
    result = dict(row)
    rooms = conn.execute(
        "SELECT room_id FROM room_payment WHERE payment_id = ?", (payment_id,)
    ).fetchall()
    result["room_ids"] = [r["room_id"] for r in rooms]
    return result


def create_payment(tenant_id: int, room_ids: list[int], amount: float,
                   due_date: str, pay_date: str = None,
                   status: str = "Pending") -> dict:
    if status not in ("Pending", "Paid", "Overdue"):
        raise ValueError("status must be 'Pending', 'Paid', or 'Overdue'")

    conn = get_connection()
    try:
        if not conn.execute("SELECT 1 FROM tenants WHERE tenant_id=?", (tenant_id,)).fetchone():
            raise ValueError(f"Tenant {tenant_id} does not exist.")
        for rid in room_ids:
            if not conn.execute("SELECT 1 FROM rooms WHERE room_id=?", (rid,)).fetchone():
                raise ValueError(f"Room {rid} does not exist.")

        cur = conn.execute(
            """INSERT INTO payments (tenant_id, amount, due_date, pay_date, status)
               VALUES (?, ?, ?, ?, ?)""",
            (tenant_id, amount, due_date, pay_date, status)
        )
        payment_id = cur.lastrowid

        conn.executemany(
            "INSERT INTO room_payment (room_id, payment_id) VALUES (?, ?)",
            [(rid, payment_id) for rid in room_ids]
        )
        conn.commit()
        return _build_payment(conn, payment_id)
    finally:
        conn.close()


def get_payment(payment_id: int) -> dict:
    conn = get_connection()
    try:
        return _build_payment(conn, payment_id)
    finally:
        conn.close()

def get_all_payments() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT payment_id FROM payments ORDER BY due_date DESC"
        ).fetchall()
        return [_build_payment(conn, r["payment_id"]) for r in rows]
    finally:
        conn.close()


def get_payments_by_tenant(tenant_id: int) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT payment_id FROM payments WHERE tenant_id = ?", (tenant_id,)
        ).fetchall()
        return [_build_payment(conn, r["payment_id"]) for r in rows]
    finally:
        conn.close()


def update_payment(payment_id: int, amount: float = None, due_date: str = None,
                   pay_date: str = None, status: str = None,
                   room_ids: list[int] = None) -> dict:
    conn = get_connection()
    try:
        fields = {}
        if amount   is not None: fields["amount"]   = amount
        if due_date is not None: fields["due_date"]  = due_date
        if pay_date is not None: fields["pay_date"]  = pay_date
        if status   is not None:
            if status not in ("Pending", "Paid", "Overdue"):
                raise ValueError("status must be 'Pending', 'Paid', or 'Overdue'")
            fields["status"] = status

        if fields:
            set_clause = ", ".join(f"{k} = ?" for k in fields)
            values = list(fields.values()) + [payment_id]
            conn.execute(f"UPDATE payments SET {set_clause} WHERE payment_id = ?", values)

        if room_ids is not None:
            for rid in room_ids:
                if not conn.execute("SELECT 1 FROM rooms WHERE room_id=?", (rid,)).fetchone():
                    raise ValueError(f"Room {rid} does not exist.")
            conn.execute("DELETE FROM room_payment WHERE payment_id = ?", (payment_id,))
            conn.executemany(
                "INSERT INTO room_payment (room_id, payment_id) VALUES (?, ?)",
                [(rid, payment_id) for rid in room_ids]
            )

        conn.commit()
        return _build_payment(conn, payment_id)
    finally:
        conn.close()


def delete_payment(payment_id: int) -> bool:
    conn = get_connection()
    try:
        cur = conn.execute(
            "DELETE FROM payments WHERE payment_id = ?", (payment_id,)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
