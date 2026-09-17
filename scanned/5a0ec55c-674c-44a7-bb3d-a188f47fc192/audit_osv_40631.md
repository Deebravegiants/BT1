# [M] Cross-origin cookies could be leaked when opening a PDF link

## Summary
Severity: Medium
Advisory: CVE-2026-53899
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-53899
Type: osv

## Details
Firefox for iOS used partial domain matching when attaching cookies to PDF requests, allowing a malicious site on a suffix domain to receive cookies belonging to the target site. This vulnerability was fixed in Firefox for iOS 152.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53899.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53899
- https://www.mozilla.org/security/advisories/mfsa2026-56/
- https://bugzilla.mozilla.org/show_bug.cgi?id=2042909
