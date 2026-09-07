# [H] Curio exposes database credentials to users with network access through verbose HTTP error responses

## Summary
Severity: High
Chain: github.com/filecoin-project/curio
Component: github.com/filecoin-project/curio
CWE: Generation of Error Message Containing Sensitive Information, Insertion of Sensitive Information into Log File
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-gj6x-q8rh-wj6x
Type: github-advisory

## Details
## Summary

Multiple HTTP handlers in Curio passed raw database error messages to HTTP clients via `http.Error()`. When the PostgreSQL/YugabyteDB driver (pgx) returned errors, these could contain the database connection string — including hostname, port, username, and password. Additionally, the internal connection string was constructed with the plaintext password embedded in the URL, which was also included in startup error messages and could surface in logs.

## Details

Three components were affected:

1. **PDP handlers** (`pdp/handlers.go`) — 18+ HTTP error paths passed `err.Error()` directly to HTTP responses. While these endpoints require ECDSA JWT authentication, an authenticated client (e.g., a FilPay service) that triggered a database error would receive the raw pgx error in the HTTP response body. Present since PDP was introduced in v1.25.1.

2. **Market mk12 deal status** (`market/mk12/mk12_utils.go`) — The `GetDealStatus` handler included `err.Error()` in error responses: `"failed to query the db for deal status: %s"`. Present since v1.24.3.

3. **Market mk20 auth middleware** (`market/mk20/http/http.go`) — Authentication error responses included `err.Error()`, potentially leaking database error details during auth flows. Present since v1.27.2.

### Root Cause

The database connection string was constructed as:
```
postgresql://username:password@host:port/database?...
```
The plaintext password was embedded directly in the URL. When pgx returned connection or query errors, the error text could contain fragments of this connection string. HTTP handlers forwarded these errors verbatim to clients.

## Impact

An attacker with network access to Curio's PDP or Market HTTP endpoints and valid authentication credentials could intentionally trigger database errors (e.g., by sending malformed requests that cause SQL failures) and extract the YugabyteDB connection credentials from the error response. With these credentials, the attacker could directly access the database, which serves as Curio's control plane.

Per Curio's [security boundary documentation](https://github.com/filecoin-project/curio/blob/main/documentation/en/design/README.md#security-boundary), these endpoints are expected to be on a trusted network. However, defense-in-depth requires that credentials are never exposed through HTTP responses regardless of network trust assumptions.

## Remediation (PR #919)

1. **Connection string password masking:** The password in the connection string is replaced with `********`. The real password is set separately via `cfg.ConnConfig.Password`, so it never appears in error messages or logs.

2. **HTTP handler sanitization:** All affected handlers now log the detailed error server-side and return a generic error message to the HTTP client.

3. **Error filter (`errFilter`):** A new function in the database layer detects and redacts any error messages containing keywords like "password", "host", "port", or "://" before they can propagate.

4. **Prometheus metrics cleanup:** Database connection metrics that could expose connection details were removed from the metrics endpoint.


_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-gj6x-q8rh-wj6x_
