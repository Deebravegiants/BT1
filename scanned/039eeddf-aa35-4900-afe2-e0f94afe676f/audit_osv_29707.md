# [M] Pluto's http.request allows CR and LF in header values

## Summary
Severity: Medium
Advisory: CVE-2024-45597
Aliases: GHSA-w8xp-pmx2-37w7
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-09-10
Source: https://osv.dev/vulnerability/CVE-2024-45597
Type: osv

## Details
Pluto is a superset of Lua 5.4 with a focus on general-purpose programming. Scripts passing user-controlled values to http.request header values are affected. An attacker could use this to send arbitrary requests, potentially leveraging authentication tokens provided in the same headers table.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45597.json
- https://github.com/PlutoLang/Pluto/security/advisories/GHSA-w8xp-pmx2-37w7
- https://nvd.nist.gov/vuln/detail/CVE-2024-45597
- https://github.com/PlutoLang/Pluto/pull/945
