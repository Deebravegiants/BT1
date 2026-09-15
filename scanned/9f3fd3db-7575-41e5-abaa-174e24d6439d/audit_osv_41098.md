# [C] CVE-2026-57532

## Summary
Severity: Critical
Advisory: CVE-2026-57532
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-57532
Type: osv

## Details
Malicious HTML content contained in the layout specification of a PDF 
ticket or badge layout was executed when the PDF editor is opened in the
 browser. This could allow one backend user to inject JavaScript into 
the browser context of another backend user. Due to requirements of the 
PDF rendering and editing libraries used, this is one of the few pages 
in our backend that do not have a strong Content-Security-Policy that 
would render this capability useless for most scenarios.

## References
- https://pypi.python.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57532.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57532
- https://github.com/pretix/pretix
- https://pretix.eu/about/en/blog/20260625-release-2026-5-2/
