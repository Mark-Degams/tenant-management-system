from Database.db import get_connection


def _row_to_dict(row) -> dict:
    return dict(row) if row else None


def create_tenant(first_name: str, last_name: str, contact_num: str,
                  birthdate: str, sex: str) -> dict:
    if sex not in ("Male", "Female", "Other"):
        raise ValueError("sex must be 'Male', 'Female', or 'Other'")
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO tenants (first_name, last_name, contact_num, birthdate, sex)
               VALUES (?, ?, ?, ?, ?)""",
            (first_name, last_name, contact_num, birthdate, sex)
        )
        conn.commit()
        return get_tenant(cur.lastrowid)
    finally:
        conn.close()


def get_tenant(tenant_id: int) -> dict:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM tenants WHERE tenant_id = ?", (tenant_id,)).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()

def get_tenant_by_name(first_name: str, last_name: str) -> dict:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM tenants WHERE first_name = ? AND last_name = ?",(first_name, last_name)).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()

def get_tenants_by_sex(sex: str) -> list[dict]:
    if sex not in ("Male", "Female", "Other"):
        raise ValueError("sex must be 'Male', 'Female', or 'Other'")
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM tenants WHERE sex = ?", (sex,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_all_tenants() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM tenants ORDER BY last_name, first_name"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_tenant(tenant_id: int, **kwargs) -> dict:
    allowed = {"first_name", "last_name", "contact_num", "birthdate", "sex"}
    fields = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not fields:
        return get_tenant(tenant_id)

    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [tenant_id]

    conn = get_connection()
    try:
        conn.execute(f"UPDATE tenants SET {set_clause} WHERE tenant_id = ?", values)
        conn.commit()
        return get_tenant(tenant_id)
    finally:
        conn.close()


def delete_tenant(tenant_id: int) -> bool:
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM tenants WHERE tenant_id = ?", (tenant_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
