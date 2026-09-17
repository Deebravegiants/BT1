# [C] CVE-2019-11691

## Summary
Severity: Critical
Advisory: CVE-2019-11691
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-11691
Type: osv

## Details
A use-after-free vulnerability can occur when working with XMLHttpRequest (XHR) in an event loop, causing the XHR main thread to be called after it has been freed. This results in a potentially exploitable crash. This vulnerability affects Thunderbird < 60.7, Firefox < 67, and Firefox ESR < 60.7.

## References
- https://www.mozilla.org/security/advisories/mfsa2019-13/
- https://www.mozilla.org/security/advisories/mfsa2019-14/
- https://www.mozilla.org/security/advisories/mfsa2019-15/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1542465
