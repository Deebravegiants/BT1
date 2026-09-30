# [C] CVE-2019-11693

## Summary
Severity: Critical
Advisory: CVE-2019-11693
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-11693
Type: osv

## Details
The bufferdata function in WebGL is vulnerable to a buffer overflow with specific graphics drivers on Linux. This could result in malicious content freezing a tab or triggering a potentially exploitable crash. *Note: this issue only occurs on Linux. Other operating systems are unaffected.*. This vulnerability affects Thunderbird < 60.7, Firefox < 67, and Firefox ESR < 60.7.

## References
- https://www.mozilla.org/security/advisories/mfsa2019-13/
- https://www.mozilla.org/security/advisories/mfsa2019-14/
- https://www.mozilla.org/security/advisories/mfsa2019-15/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1532525
