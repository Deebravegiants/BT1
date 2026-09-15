# [M] SpiceDB's SPICEDB_DATASTORE_CONN_URI is leaked on startup logs

## Summary
Severity: Medium
Advisory: GHSA-jf4f-rr2c-9m58
CVE: CVE-2026-40091
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-jf4f-rr2c-9m58
Type: github-advisory

## Affected
- Go: `github.com/authzed/spicedb` — affected >=1.49.0 <1.51.1

## Details
### Impact
When SpiceDB starts with log level `info`, the startup `"configuration"` log will include the full datastore DSN, including the plaintext password, inside `DatastoreConfig.URI`.

### Patches
v1.51.1

### Workarounds
Change the log level to `warn` or `error`.

## References
- https://github.com/authzed/spicedb/security/advisories/GHSA-jf4f-rr2c-9m58
- https://nvd.nist.gov/vuln/detail/CVE-2026-40091
- https://github.com/authzed/spicedb
- https://github.com/authzed/spicedb/releases/tag/v1.51.1
