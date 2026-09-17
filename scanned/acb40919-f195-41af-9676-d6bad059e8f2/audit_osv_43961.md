# [M] Grav before 2.0.16 Information Disclosure via offsetGet

## Summary
Severity: Medium
Advisory: CVE-2026-76839
Aliases: GHSA-3jhr-mxmx-38cx
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-76839
Type: osv

## Details
Grav before 2.0.16 allows sandboxed Twig templates to access sensitive User fields through allow-listed offsetGet() and offsetexists() methods that lack field filtering. Attackers with page-edit permissions can call offsetGet() on User objects to extract hashed passwords and 2FA secrets, enabling offline password cracking and authentication bypass.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76839.json
- https://github.com/getgrav/grav/security/advisories/GHSA-3jhr-mxmx-38cx
- https://nvd.nist.gov/vuln/detail/CVE-2026-76839
- https://www.vulncheck.com/advisories/grav-before-information-disclosure-via-offsetget
