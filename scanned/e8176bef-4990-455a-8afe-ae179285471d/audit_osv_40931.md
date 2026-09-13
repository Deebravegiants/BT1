# [C] Capgo - Subkey Scope Bypass in middlewareKey via x-limited-key-id Header

## Summary
Severity: Critical
Advisory: CVE-2026-56232
Aliases: GHSA-2h89-vcvx-5pvh
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-56232
Type: osv

## Details
Capgo before 12.128.2 fails to enforce limited_to_orgs and limited_to_apps constraints on subkeys provided via x-limited-key-id header in middlewareKey function. Attackers can bypass subkey scope restrictions by referencing their own subkeys, causing all downstream route handlers to use the unrestricted parent key instead of the scoped subkey.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56232.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-2h89-vcvx-5pvh
- https://nvd.nist.gov/vuln/detail/CVE-2026-56232
- https://www.vulncheck.com/advisories/capgo-subkey-scope-bypass-in-middlewarekey-via-x-limited-key-id-header
