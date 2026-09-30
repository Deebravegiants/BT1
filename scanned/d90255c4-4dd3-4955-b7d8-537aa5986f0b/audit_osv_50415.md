# [M] CVE-2020-15664

## Summary
Severity: Medium
Advisory: CVE-2020-15664
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2020-10-01
Source: https://osv.dev/vulnerability/CVE-2020-15664
Type: osv

## Details
By holding a reference to the eval() function from an about:blank window, a malicious webpage could have gained access to the InstallTrigger object which would allow them to prompt the user to install an extension. Combined with user confusion, this could result in an unintended or malicious extension being installed. This vulnerability affects Firefox < 80, Thunderbird < 78.2, Thunderbird < 68.12, Firefox ESR < 68.12, Firefox ESR < 78.2, and Firefox for Android < 80.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-41/
- https://www.mozilla.org/security/advisories/mfsa2020-36/
- https://www.mozilla.org/security/advisories/mfsa2020-37/
- https://www.mozilla.org/security/advisories/mfsa2020-38/
- https://www.mozilla.org/security/advisories/mfsa2020-39/
- https://www.mozilla.org/security/advisories/mfsa2020-40/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1658214
