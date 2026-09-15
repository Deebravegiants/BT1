# [M] Improper Restriction of XML External Entity Reference in Inkscape

## Summary
Severity: Medium
Advisory: CVE-2026-4980
CVSS: 6.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-4980
Type: osv

## Details
A local file disclosure vulnerability in the XInclude processing component of Inkscape 1.1 before 1.3 allows a remote attacker to read local files via a crafted SVG file containing malicious xi:include tags.

## References
- https://gitlab.com/inkscape/inkscape/-/work_items/3557
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4980.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-4980
- https://gitlab.com/inkscape/inkscape/-/merge_requests/5269
