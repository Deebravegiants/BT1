# [H] CVE-2021-23981

## Summary
Severity: High
Advisory: CVE-2021-23981
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2021-03-31
Source: https://osv.dev/vulnerability/CVE-2021-23981
Type: osv

## Details
A texture upload of a Pixel Buffer Object could have confused the WebGL code to skip binding the buffer used to unpack it, resulting in memory corruption and a potentially exploitable information leak or crash. This vulnerability affects Firefox ESR < 78.9, Firefox < 87, and Thunderbird < 78.9.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-11/
- https://www.mozilla.org/security/advisories/mfsa2021-12/
- https://www.mozilla.org/security/advisories/mfsa2021-10/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1692832
