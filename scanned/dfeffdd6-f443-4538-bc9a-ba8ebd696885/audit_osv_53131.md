# [M] CVE-2022-3034

## Summary
Severity: Medium
Advisory: CVE-2022-3034
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-3034
Type: osv

## Details
When receiving an HTML email that specified to load an <code>iframe</code> element from a remote location, a request to the remote document was sent. However, Thunderbird didn't display the document. This vulnerability affects Thunderbird < 102.2.1 and Thunderbird < 91.13.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-38/
- https://www.mozilla.org/security/advisories/mfsa2022-39/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1745751
