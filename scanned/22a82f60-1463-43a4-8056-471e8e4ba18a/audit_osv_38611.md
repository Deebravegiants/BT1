# [H] CVE-2026-40960

## Summary
Severity: High
Advisory: CVE-2026-40960
Aliases: GHSA-22c4-238c-m5j4
CVSS: 8.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-40960
Type: osv

## Details
Luanti 5 before 5.15.2 sometimes allows unintended access to an insecure environment. If at least one mod is listed as secure.trusted_mods or secure.http_mods, then a crafted mod can intercept the request for the insecure environment or HTTP API, and also receive access to it.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40960.json
- https://github.com/luanti-org/luanti/security/advisories/GHSA-22c4-238c-m5j4
- https://nvd.nist.gov/vuln/detail/CVE-2026-40960
- https://github.com/luanti-org/luanti/commit/0faf529bc4b89e70a275ed1162047815118f2413
- https://github.com/luanti-org/luanti/commit/827fd4cf7f989482b2dad381fa4afd642ea73e8c
