# [H] CVE-2020-6806

## Summary
Severity: High
Advisory: CVE-2020-6806
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-03-25
Source: https://osv.dev/vulnerability/CVE-2020-6806
Type: osv

## Details
By carefully crafting promise resolutions, it was possible to cause an out-of-bounds read off the end of an array resized during script execution. This could have led to memory corruption and a potentially exploitable crash. This vulnerability affects Thunderbird < 68.6, Firefox < 74, Firefox < ESR68.6, and Firefox ESR < 68.6.

## References
- https://usn.ubuntu.com/4328-1/
- https://usn.ubuntu.com/4335-1/
- https://www.mozilla.org/security/advisories/mfsa2020-08/
- https://www.mozilla.org/security/advisories/mfsa2020-09/
- https://www.mozilla.org/security/advisories/mfsa2020-10/
- http://packetstormsecurity.com/files/157524/Firefox-js-ReadableStreamCloseInternal-Out-Of-Bounds-Access.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1612308
