# [H] CVE-2022-43140

## Summary
Severity: High
Advisory: CVE-2022-43140
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-11-17
Source: https://osv.dev/vulnerability/CVE-2022-43140
Type: osv

## Details
kkFileView v4.1.0 was discovered to contain a Server-Side Request Forgery (SSRF) via the component cn.keking.web.controller.OnlinePreviewController#getCorsFile. This vulnerability allows attackers to force the application to make arbitrary requests via injection of crafted URLs into the url parameter.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43140.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43140
- https://github.com/kekingcn/kkFileView/issues/392
