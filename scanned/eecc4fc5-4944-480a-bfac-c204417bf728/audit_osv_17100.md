# [M] CVE-2020-12414

## Summary
Severity: Medium
Advisory: CVE-2020-12414
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2020-07-09
Source: https://osv.dev/vulnerability/CVE-2020-12414
Type: osv

## Details
IndexedDB should be cleared when leaving private browsing mode and it is not, the API for WKWebViewConfiguration was being used incorrectly and requires the private instance of this object be deleted when leaving private mode. This vulnerability affects Firefox for iOS < 27.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-23/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1646756
