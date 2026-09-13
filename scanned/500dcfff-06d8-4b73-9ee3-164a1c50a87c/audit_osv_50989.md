# [H] CVE-2020-6811

## Summary
Severity: High
Advisory: CVE-2020-6811
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-03-25
Source: https://osv.dev/vulnerability/CVE-2020-6811
Type: osv

## Details
The 'Copy as cURL' feature of Devtools' network tab did not properly escape the HTTP method of a request, which can be controlled by the website. If a user used the 'Copy as Curl' feature and pasted the command into a terminal, it could have resulted in command injection and arbitrary command execution. This vulnerability affects Thunderbird < 68.6, Firefox < 74, Firefox < ESR68.6, and Firefox ESR < 68.6.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-09/
- https://www.mozilla.org/security/advisories/mfsa2020-10/
- https://usn.ubuntu.com/4328-1/
- https://usn.ubuntu.com/4335-1/
- https://www.mozilla.org/security/advisories/mfsa2020-08/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1607742
