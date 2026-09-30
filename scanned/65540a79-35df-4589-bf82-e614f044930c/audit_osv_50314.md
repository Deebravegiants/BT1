# [M] CVE-2020-12392

## Summary
Severity: Medium
Advisory: CVE-2020-12392
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-05-26
Source: https://osv.dev/vulnerability/CVE-2020-12392
Type: osv

## Details
The 'Copy as cURL' feature of Devtools' network tab did not properly escape the HTTP POST data of a request, which can be controlled by the website. If a user used the 'Copy as cURL' feature and pasted the command into a terminal, it could have resulted in the disclosure of local files. This vulnerability affects Firefox ESR < 68.8, Firefox < 76, and Thunderbird < 68.8.0.

## References
- https://security.gentoo.org/glsa/202005-03
- https://security.gentoo.org/glsa/202005-04
- https://usn.ubuntu.com/4373-1/
- https://www.mozilla.org/security/advisories/mfsa2020-16/
- https://www.mozilla.org/security/advisories/mfsa2020-17/
- https://www.mozilla.org/security/advisories/mfsa2020-18/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1614468
