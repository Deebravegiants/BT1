# [M] FreshRSS: Double clickjacking can lead to privilege escalation

## Summary
Severity: Medium
Advisory: CVE-2025-59950
Aliases: GHSA-j66v-hvqx-5vh3
CVSS: 6.7 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:L)
Published: 2025-09-29
Source: https://osv.dev/vulnerability/CVE-2025-59950
Type: osv

## Details
FreshRSS is a free, self-hostable RSS aggregator. In versions 1.26.3 and below, due to a bypass of double clickjacking protection (confirmation dialog), it is possible to trick the admin into clicking the Promote button in another user's management page after the admin double clicks on a button inside an attacker-controlled website. A successful attack can allow the attacker to promote themselves to "admin" and log into other users' accounts; the attacker has to know the specific instance URL they're targeting. This issue is fixed in version 1.27.0.

## References
- https://github.com/FreshRSS/FreshRSS/releases/tag/1.27.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59950.json
- https://github.com/FreshRSS/FreshRSS/security/advisories/GHSA-j66v-hvqx-5vh3
- https://nvd.nist.gov/vuln/detail/CVE-2025-59950
- https://github.com/FreshRSS/FreshRSS/pull/7771
