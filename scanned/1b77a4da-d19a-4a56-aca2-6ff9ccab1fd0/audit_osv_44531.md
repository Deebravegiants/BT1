# [M] openSIS Classic 9.3 - Insecure Direct Object Reference in Sent Mail

## Summary
Severity: Medium
Advisory: CVE-2026-8406
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-8406
Type: osv

## Details
openSIS Classic 9.3 contains an insecure direct object reference vulnerability in the messaging module. Any authenticated user with access to the messaging module can request sent-message details from modules/messaging/SentMail.php by supplying an arbitrary mail_id value.

## References
- https://fluidattacks.com/es/advisories/melanie
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8406.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8406
- https://github.com/OS4ED/openSIS-Classic/commit/c45d43146167324bae06bdf09de3e4bd2e5e478f
- https://github.com/OS4ED/openSIS-Classic
