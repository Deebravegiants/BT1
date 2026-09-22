# [M] CVE-2021-23984

## Summary
Severity: Medium
Advisory: CVE-2021-23984
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2021-03-31
Source: https://osv.dev/vulnerability/CVE-2021-23984
Type: osv

## Details
A malicious extension could have opened a popup window lacking an address bar. The title of the popup lacking an address bar should not be fully controllable, but in this situation was. This could have been used to spoof a website and attempt to trick the user into providing credentials. This vulnerability affects Firefox ESR < 78.9, Firefox < 87, and Thunderbird < 78.9.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-10/
- https://www.mozilla.org/security/advisories/mfsa2021-11/
- https://www.mozilla.org/security/advisories/mfsa2021-12/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1693664
