# [H] CVE-2024-43033

## Summary
Severity: High
Advisory: CVE-2024-43033
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-22
Source: https://osv.dev/vulnerability/CVE-2024-43033
Type: osv

## Details
JPress through 5.1.1 on Windows has an arbitrary file upload vulnerability that could cause arbitrary code execution via ::$DATA to AttachmentController, such as a .jsp::$DATA file to io.jpress.web.commons.controller.AttachmentController#upload. NOTE: this is unrelated to the attack vector for CVE-2024-32358.

## References
- https://cwe.mitre.org/data/definitions/69.html
- https://github.com/lazy-forever/CVE-Reference/tree/main/2024/43033
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43033.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43033
- https://github.com/JPressProjects/jpress/issues/188
