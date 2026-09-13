# [M] OwnTone Server < 29.1 Race Condition DoS via DAAP Login

## Summary
Severity: Medium
Advisory: CVE-2026-41458
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-41458
Type: osv

## Details
OwnTone Server versions 28.4 through 29.0 contain a race condition vulnerability in the DAAP login handler that allows unauthenticated attackers to crash the server by exploiting unsynchronized access to the global DAAP session list. Attackers can flood the DAAP /login endpoint with concurrent requests to trigger a remote denial of service condition without requiring authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41458.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41458
- https://www.vulncheck.com/advisories/owntone-server-race-condition-dos-via-daap-login
- https://github.com/owntone/owntone-server/pull/1980
- https://github.com/owntone/owntone-server/commit/dca94641a5ed66500822dd51281774794cdb6c22
- https://github.com/owntone/owntone-server
