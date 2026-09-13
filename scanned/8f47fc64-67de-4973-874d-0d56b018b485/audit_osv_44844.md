# [M] Snipe-IT before 8.7.0 Server-Side Request Forgery via employee_num

## Summary
Severity: Medium
Advisory: CVE-2026-86771
Aliases: GHSA-73xg-j94v-gjcf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:N/VA:L/SC:H/SI:N/SA:L)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86771
Type: osv

## Details
Snipe-IT versions before 8.7.0 fail to HTML-escape the employee_num field in the acceptance PDF generator, allowing attackers with users.edit permission to inject img tags into TCPDF's writeHTML() function. Attackers can craft a malicious employee_num value containing an img tag with an arbitrary HTTP(S) URL to trigger server-side requests to internal services, cloud metadata endpoints, or external targets when a victim signs an asset acceptance.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86771.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-73xg-j94v-gjcf
- https://nvd.nist.gov/vuln/detail/CVE-2026-86771
- https://www.vulncheck.com/advisories/snipe-it-before-8.7.0-server-side-request-forgery-via-employee-num
