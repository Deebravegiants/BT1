# [H] @executeautomation/database-server does not properly restrict access, bypassing a "read-only" mode

## Summary
Severity: High
Advisory: GHSA-65hm-pwj5-73pw
CVE: CVE-2025-59333
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2025-09-16
Source: https://github.com/advisories/GHSA-65hm-pwj5-73pw
Type: github-advisory

## Affected
- npm: `@executeautomation/database-server` — affected >=0

## Details
The MCP Server provided by ExecuteAutomation at https://github.com/executeautomation/mcp-database-server provides an MCP interface for agentic workflows to interact with different kinds of database servers such as PostgreSQL database. However, the `mcp-database-server` MCP Server distributed via the npm package `@executeautomation/database-server` fails to implement proper security control that properly enforce a "read-only" mode and as such it is vulnerable to abuse and attacks on the affected database servers such as PostgreSQL (and potentially other db servers that expose elevated functionalities) and which may result in denial of service and other unexpected behavior.

This MCP Server is also publicly published in the npm registry: https://www.npmjs.com/package/@executeautomation/database-server

## Vulnerable code

The vulnerable code to SQL injection takes shape in several ways:
- `startsWith("SELECT")` can include multiple queries because the pg driver for the `client.query()` supports multi queries if terminated with a `;`
- `startsWith("SELECT")` can include denial of service queries for stored procedures and other internal db functions

The tool call [here in index.ts](https://github.com/executeautomation/mcp-database-server/blob/d6afa4be08eb05343195635fa9462746a6be3a59/index.ts#L272C1-L291C6) is vulnerable:

```
// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  switch (request.params.name) {
    case "read_query": {
      const query = request.params.arguments?.query as string;
      
      if (!query.trim().toLowerCase().startsWith("select")) {
        throw new Error("Only SELECT queries are allowed with read_query");
      }

      try {
        const result = await dbAll(query);
        return {
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          isError: false,
        };
      } catch (error: any) {
        throw new Error(`SQL Error: ${error.message}`);
      }
    }
```

The MCP Server exposes the tool `read_query` with a naive attempt to guard for exclusive "read-only" mode that allows only data retrieval from the server by performing a check on the provided query string to ensure that it starts with a "SELECT" query.

In short, the code check `startWith("select")` is not an adequate security control to strict for read-only mode queries and can be abused for side-effects and database-level operations.

## Exploitation

While allowing only `SELECT` type queries might seem like a good defense to allow only data retrieval and not data manipulation in any way (hence, "read-only" mode), it is a non-suficient way of protecting against database servers that expose extra functionality through internal function calls.

Several examples that will allow side effects through `SELECT` queries:
1. Stored procedures: `SELECT some_function_that_updates_data();`
2. Internal database administrative operations: `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE ...;`

Even when the database is known not to have any stored procedures defined, an attacker can still cause significant availability and service disruption by executing `pg_terminate_backend()`.

Following is a reproduction:

- Simulate a long-running query, for example: `query = "SELECT pg_sleep(5 * 60)"`
- Now, from the MCP programmatic interface, execute the following query `SELECT pid, usename, state, query FROM  pg_stat_activity;` to get the PID for the long running query
- Next, use the same MCP interface to then request to run the following query: `SELECT pg_terminate_backend(PID);` and observe the long running query is now terminated

Similar database side-effects may be found in MySQL or SQLite.

## Impact

The above exploitation surfaces two significant security risks: a denial of service that affects availability and confidentiality dislcosure that allows users unauthorized access to queries running on the server and potential leak of data.

## Recommendation

- Don't rely solely on the "starts with" `SELECT`
- Strict access to specific tables that the user is only authorized to query for
- Do not allow multiple SQL queries to be chained together like `SELECT * ...; INSERT INTO ...`
- Require users that adopt this MCP Server to use fine-grained permissions on the database server with strict and explicit access to specific capabilities on the server.

## CVE Details

Recommended CWE: CWE-284: Improper Access Control
Recommendec CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H

## References and Prior work

1. GitHub Kanban MCP Server found [vulnerable to command injection](https://github.com/advisories/GHSA-6jx8-rcjx-vmwf).
2. iOS Simulator MCP Server found [vulnerable to command injection](https://github.com/advisories/GHSA-6f6r-m9pv-67jw).
3. Liran's [Node.js Secure Coding](https://www.nodejs-security.com/book/command-injection) for educational materials on injection attacks and secure coding practices.
4. [How to Bypass Access Control in PostgreSQL in Simple PSQL MCP Server for SQL Injection](https://www.nodejs-security.com/blog/how-to-bypass-access-control-in-postgresql-in-simple-psql-mcp-server-for-sql-injection)
5. Reference example from prior security research on this topic, demonstrating how vulnerable MCP Server connected to Cursor is abused with prompt injection to bypass the developer's intended logic:

![Cursor defined MCP Server vulnerable to command injection](https://res.cloudinary.com/snyk/image/upload/f_auto,w_2560,q_auto/v1747081395/Screenshot_2025-05-07_at_9.22.11_AM_d76kvm.png)

## Credit

Disclosed by [Liran Tal](https://lirantal.com)

## References
- https://github.com/executeautomation/mcp-database-server/security/advisories/GHSA-65hm-pwj5-73pw
- https://nvd.nist.gov/vuln/detail/CVE-2025-59333
- https://github.com/executeautomation/mcp-database-server
