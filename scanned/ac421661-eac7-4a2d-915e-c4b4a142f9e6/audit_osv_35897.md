# [M] ReDoS in Open Mercato

## Summary
Severity: Medium
Advisory: CVE-2026-16270
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/CVE-2026-16270
Type: osv

## Details
Open Mercato does not validate regex rules. An attacker with privileges to create the regex rule can add an unsafe regex to a field. When someone provide the proper string it can result in a DoS attack.


This issue was fixed in version 0.6.4.

## References
- https://www.openmercato.com/
- https://cert.pl/posts/2026/07/CVE-2026-16270
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16270.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-16270
- https://github.com/open-mercato/open-mercato/pull/1996
- https://github.com/open-mercato/open-mercato
