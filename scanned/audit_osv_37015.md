# [M] calibre Vulnerable to HTTP Response Header Injection

## Summary
Severity: Medium
Advisory: CVE-2026-27810
Aliases: GHSA-5fpj-fxw7-8grw
CVSS: 6.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-27810
Type: osv

## Details
calibre is a cross-platform e-book manager for viewing, converting, editing, and cataloging e-books. Prior to version 9.4.0, an HTTP Response Header Injection vulnerability in the calibre Content Server allows any authenticated user to inject arbitrary HTTP headers into server responses via an unsanitized `content_disposition` query parameter in the `/get/` and `/data-files/get/` endpoints. All users running the calibre Content Server with authentication enabled are affected. The vulnerability is exploitable by any authenticated user and can also be triggered by tricking an authenticated victim into clicking a crafted link. Version 9.4.0 contains a fix for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27810.json
- https://github.com/kovidgoyal/calibre/security/advisories/GHSA-5fpj-fxw7-8grw
- https://nvd.nist.gov/vuln/detail/CVE-2026-27810
