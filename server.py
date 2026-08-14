from mcp.server import MCPServer
from database import get_connection

mcp = MCPServer("Job Tracker MCP")


@mcp.resource("schema://applications")
def applications_schema() -> list[dict]:
    """Return the current schema of the applications table."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    column_name,
                    data_type,
                    is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'applications'
                ORDER BY ordinal_position;
            """)

            rows = cur.fetchall()

    return [
        {
            "column": row[0],
            "type": row[1],
            "nullable": row[2],
        }
        for row in rows
    ]

@mcp.tool()
def list_applications() -> list[dict]:
    """Return all job applications."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id,
                    title,
                    description,
                    link,
                    apply_date,
                    status
                FROM applications
                ORDER BY apply_date DESC;
            """)

            rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "link": row[3],
            "apply_date": str(row[4]) if row[4] else None,
            "status": row[5],
        }
        for row in rows
    ]


@mcp.tool()
def get_application(application_id: int) -> dict:
    """Return one job application by its ID."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id,
                    title,
                    description,
                    link,
                    apply_date,
                    status
                FROM applications
                WHERE id = %s;
            """, (application_id,))

            row = cur.fetchone()

    if row is None:
        return {
            "error": f"Application {application_id} not found"
        }

    return {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "link": row[3],
        "apply_date": str(row[4]) if row[4] else None,
        "status": row[5],
    }

@mcp.tool()
def create_application(
    title: str,
    description: str | None = None,
    link: str | None = None,
    apply_date: str | None = None,
    status: str | None = None,
) -> dict:
    """Create a new job application."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO applications (
                    title,
                    description,
                    link,
                    apply_date,
                    status
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, title, description, link, apply_date, status;
            """, (
                title,
                description,
                link,
                apply_date,
                status,
            ))

            row = cur.fetchone()

    return {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "link": row[3],
        "apply_date": str(row[4]) if row[4] else None,
        "status": row[5],
    }

if __name__ == "__main__":
    mcp.run()