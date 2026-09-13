# [H] Dragonfly: RESTORE operations may crash the server

## Summary
Severity: High
Advisory: CVE-2026-54341
Aliases: GHSA-cwjr-j869-h8q9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-54341
Type: osv

## Details
Dragonfly is an in-memory data store built for modern application workloads. Prior to 1.39.0, a crafted RESTORE payload triggers an out-of-bounds read in DragonflyDB's listpack collection loaders, crashing the entire server process (SIGSEGV). Because DragonflyDB requires no authentication by default and RESTORE is a normal keyspace command, an unauthenticated remote attacker can crash the server with a single ~24-byte command — a remote, repeatable denial of service. This vulnerability is fixed in 1.39.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54341.json
- https://github.com/dragonflydb/dragonfly/security/advisories/GHSA-cwjr-j869-h8q9
- https://nvd.nist.gov/vuln/detail/CVE-2026-54341
- https://github.com/dragonflydb/dragonfly/pull/7502
