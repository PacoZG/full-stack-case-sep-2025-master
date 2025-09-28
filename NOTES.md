# Notes and comments

Add any possible comments or notes on your solution here

## Alembic Migrations (Database Schema Management)

### How to use Alembic for Database Migrations

Alembic is used to manage database schema changes in a version-controlled manner. This ensures that your database schema can evolve alongside your application code and remains consistent across different environments.

**1. Start your Docker containers:**
   Ensure your backend and database services are running:
   ```bash
   docker compose watch
   ```

**2. Generate a new migration (if schema changes have been made):**
   If you've made changes to your SQLAlchemy models (e.g., added a new table, column, or modified an existing one), Alembic can automatically detect these changes and generate a migration script.
   ```bash
   docker-compose exec backend alembic revision --autogenerate -m "Descriptive message for your changes"
   ```
   This command will create a new Python file in `backend/app/alembic/versions/` detailing the schema changes. Review this file to ensure it accurately reflects your intended changes.

**3. Apply pending migrations to the database:**
   To apply all migrations (including newly generated ones or any that haven't been applied yet) to your database, run:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```
   This command will bring your database schema up to the latest version defined by your migration scripts.

### Why use Alembic Migrations?

*   **Version Control for Database Schema:** Treat your database schema changes like code changes, allowing you to track, review, and revert them.
*   **Environment Consistency:** Ensure that your development, staging, and production environments all have the same database schema, reducing "it works on my machine" issues.
*   **Automated Schema Evolution:** Automate the process of updating your database schema, which is crucial for continuous integration and deployment workflows.
*   **Rollback Capability:** Easily revert to a previous database schema version if issues arise with a new migration.

## Backend API: File Upload & Signal Data Processing

### Overview
This section documents the steps and components involved in creating the API for uploading and processing signal data files in the backend.

### 1. Database Models
- Added `UploadedFile` and `SignalMeasurement` models in `backend/app/models.py`.
  - `UploadedFile` stores metadata about each uploaded file (filename, upload time, status, type).
  - `SignalMeasurement` stores parsed signal data, linked to an `UploadedFile`.

### 2. API Endpoints
- Implemented in `backend/app/api/routes/signal_data.py`:
  - `POST /upload-signal-data`: Accepts file uploads (CSV or binary), saves metadata, and triggers background processing.
  - `GET /uploaded-files`: Lists all uploaded files and their status.
  - `GET /uploaded-files/{file_id}`: Fetches details/status for a single uploaded file.

### 3. File Parsing & Processing
- Parsing logic in `backend/app/services/signal_parser.py`:
  - `parse_csv_file`: Handles CSV files, normalizes field names, extracts required fields, and creates `SignalMeasurement` records.
  - `parse_binary_file`: Placeholder for binary parsing; can be extended for real binary formats.
  - `process_signal_file`: Dispatches to the correct parser, saves parsed data to the database, and updates file status.

### 4. Logging & Error Handling
- Added logging to `signal_parser.py`:
  - Logs errors and successful parses to `signal_parser.log` for debugging and monitoring.
  - Updates file status to indicate success, failure, or no data.

### 5. Extensibility & Robustness
- CSV parser supports field name variations and ignores extra fields.
- Binary parser is designed to be easily extended for new formats.
- System is designed for future extensibility (new file types, schema changes).

### 6. Testing & Validation
- All changes validated with backend tests and manual uploads.
- Error handling ensures robust operation and clear status reporting.

### 7. Documentation
- API and backend logic are documented in this file and in the codebase for future maintainers.

## Frontend: Registering New Routes and Layout Integration

### How to Add a New Route (e.g., /signal-data) in TanStack Router

1. **Create the Route File:**
   - Add a new file in `src/routes/_layout/` (e.g., `src/routes/_layout/signal-data.tsx`).
   - Export the route using `createFileRoute('/_layout/signal-data')` and render your component (e.g., `SignalData`).
   - This ensures the route is a child of the main layout and inherits navigation/sidebar, just like `/items` and `/settings`.

2. **Component Consistency:**
   - For tables and other UI, use the same design system components as in other management pages (e.g., use `Table.Root`, `Table.Header`, `Table.Row`, `Table.ColumnHeader`, `Table.Body`, `Table.Cell` for tables, matching `items.tsx`).
   - This ensures a unified look and feel across the app.

3. **Navigation:**
   - Add a sidebar or navbar link to `/signal-data` so users can access the new page easily.

4. **Remove Top-Level Route (if needed):**
   - If you previously had a top-level `src/routes/signal-data.tsx`, you can remove it to avoid duplicate routes and ensure only the layout-wrapped version is used.

### Example: Registering /signal-data in the Layout
```tsx
// src/routes/_layout/signal-data.tsx
import { createFileRoute } from '@tanstack/react-router';
import SignalData from '../signal-data';

export const Route = createFileRoute('/_layout/signal-data')({
  component: SignalData,
});
```

### Example: Table Usage for Consistency
```tsx
<Table.Root size={{ base: "sm", md: "md" }}>
  <Table.Header>
    <Table.Row>
      <Table.ColumnHeader w="sm">Filename</Table.ColumnHeader>
      ...
    </Table.Row>
  </Table.Header>
  <Table.Body>
    {data.map((row) => (
      <Table.Row key={row.id}>
        <Table.Cell>{row.filename}</Table.Cell>
        ...
      </Table.Row>
    ))}
  </Table.Body>
</Table.Root>
```

### Why This Matters
- Ensures all management pages (items, signal data, etc.) share the same layout, navigation, and design system.
- Makes the app easier to maintain and extend.
- Guarantees a consistent user experience.

## Missing Features and Findings

### Backend
- Database migrations were configured to ensure data availability and schema evolution.
- The OpenAPI schema in the backend was updated to reflect new endpoints and models.
- API endpoints were created for file upload, access, and management.

### Frontend
- A user-facing component was created for uploading files.
- The upload component is accessible via a new link in the sidebar for easy navigation.

### Missing Features
- The new service layer for the frontend (to create, edit, and fetch files using autogenerated client code) is not yet configured.
- The main blocker is the inability to generate these services using the `generate-client.sh` script, due to backend dependency/version issues.

### Findings
- Some dependencies in both the frontend and backend are slightly outdated, and some have deprecated or changed APIs. This increased the time required for development and troubleshooting.

### Conclusion and Personal Reflection
- With no prior Python experience, I relied heavily on AI agents to understand and resolve backend issues.
- On the frontend, I spent significant time learning and experimenting with libraries like TanStack Router and Chakra UI, which, while not overly complex, required careful study to integrate properly.
- Although I was unable to deliver a fully working end-to-end solution, this challenge introduced me to new tools and workflows, and I appreciate the opportunity to learn and grow from the experience.
