from Database.db import get_connection

def _row_to_dict(row) -> dict:
    return dict(row) if row else None


def create_room(room_num: str, room_type: str, capacity: int, deposit: float,
                rent_summer: float, rent_regular: float) -> dict:
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO rooms (room_num, room_type, capacity, deposit, rent_summer, rent_regular)
               VALUES (?, ?, ?, ?, ?)""",
            (room_num, room_type, capacity, deposit, rent_summer, rent_regular)
        )
        conn.commit()
        return get_room_by_id(cur.lastrowid)
    finally:
        conn.close()


def get_room_by_id(room_id: int) -> dict:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM rooms WHERE room_id = ?", (room_id,)).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()

def get_room_by_num(room_num: str) -> dict:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM rooms WHERE room_num = ?", (room_num,)).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()

def get_rooms_by_type(room_type: str) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM rooms WHERE room_type = ?", (room_type,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_all_rooms() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM rooms ORDER BY room_num").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def update_room(room_id: int, **kwargs) -> dict:
    allowed = {"room_num", "capacity", "deposit", "rent_summer", "rent_regular"}
    fields = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not fields:
        return get_room_by_id(room_id)

    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [room_id]

    conn = get_connection()
    try:
        conn.execute(f"UPDATE rooms SET {set_clause} WHERE room_id = ?", values)
        conn.commit()
        return get_room_by_id(room_id)
    finally:
        conn.close()


def delete_room(room_id: int) -> bool:
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM rooms WHERE room_id = ?", (room_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()