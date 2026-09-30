# [C] CVE-2019-9790

## Summary
Severity: Critical
Advisory: CVE-2019-9790
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-26
Source: https://osv.dev/vulnerability/CVE-2019-9790
Type: osv

## Details
A use-after-free vulnerability can occur when a raw pointer to a DOM element on a page is obtained using JavaScript and the element is then removed while still in use. This results in a potentially exploitable crash. This vulnerability affects Thunderbird < 60.6, Firefox ESR < 60.6, and Firefox < 66.

## References
- https://access.redhat.com/errata/RHSA-2019:1144
- https://www.mozilla.org/security/advisories/mfsa2019-07/
- https://www.mozilla.org/security/advisories/mfsa2019-08/
- https://www.mozilla.org/security/advisories/mfsa2019-11/
- https://access.redhat.com/errata/RHSA-2019:0966
- https://bugzilla.mozilla.org/show_bug.cgi?id=1525145
