# [M] Data exposed without proper permission

## Summary
Severity: Medium
Advisory: CVE-2026-11764
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N/E:U)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-11764
Type: osv

## Details
When creating an export of all reusable media, the secrets of connected 
gift cards were included in the export even if the user creating the 
export does not have permission to view gift cards. This is inconsistent
 with the UI and API where only the first letters of the gift card 
secret are shown. Therefore, it allows circumventing a permission 
boundary.

## References
- https://pypi.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11764.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11764
- https://pretix.eu/about/en/blog/20260609-release-2026-5-1/
- https://github.com/pretix/pretix
