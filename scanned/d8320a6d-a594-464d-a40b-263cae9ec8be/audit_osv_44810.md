# [H] knowns before 0.30.0 Path Traversal via Import Name

## Summary
Severity: High
Advisory: CVE-2026-86542
Aliases: GHSA-wh3c-v55g-qfg8
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-86542
Type: osv

## Details
knowns before 0.30.0 fails to validate import names in the import routes, allowing unauthenticated attackers to write files outside the imports directory. Attackers can supply traversal sequences in the name parameter to escape the imports directory and overwrite arbitrary files writable by the server process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86542.json
- https://github.com/knowns-dev/knowns/releases/tag/v0.30.0
- https://github.com/knowns-dev/knowns/security/advisories/GHSA-wh3c-v55g-qfg8
- https://nvd.nist.gov/vuln/detail/CVE-2026-86542
- https://www.vulncheck.com/advisories/knowns-before-0.30.0-path-traversal-via-import-name
- https://github.com/knowns-dev/knowns/commit/d3989829fb5095666d23d005b2f78a082832a396
- https://github.com/knowns-dev/knowns/blob/v0.29.1/internal/server/routes/imports.go#L376-L420
- https://github.com/knowns-dev/knowns/blob/v0.29.1/internal/server/routes/imports.go#L519-L551
