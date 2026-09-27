# [C] MISP organization administrators can target site administrator accounts for password reset

## Summary
Severity: Critical
Advisory: CVE-2026-54358
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-54358
Type: osv

## Details
An incorrect authorization vulnerability in MISP allows an organization administrator to target site administrator accounts belonging to the same organization through the administrative email functionality. The affected code restricted organization administrators to users within their own organization, but did not exclude accounts assigned a site administrator role from recipient queries. As a result, an organization administrator could perform privileged account-management actions, such as initiating a password reset workflow, against a higher-privileged site administrator account in the same organization.

Successful exploitation may allow an authenticated organization administrator to interfere with or potentially take over a site administrator account, resulting in privilege escalation and full compromise of the MISP instance’s confidentiality, integrity, and availability.

Attack prerequisites:
The attacker must be authenticated as an organization administrator in the same organization as a site administrator account.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54358.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-54358
- https://github.com/MISP/MISP/commit/146795489abef478c8f595ecde2501c32482b81e
