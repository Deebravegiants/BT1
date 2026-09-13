# [C] CVE-2022-26384

## Summary
Severity: Critical
Advisory: CVE-2022-26384
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-26384
Type: osv

## Details
If an attacker could control the contents of an iframe sandboxed with <code>allow-popups</code> but not <code>allow-scripts</code>, they were able to craft a link that, when clicked, would lead to JavaScript execution in violation of the sandbox. This vulnerability affects Firefox < 98, Firefox ESR < 91.7, and Thunderbird < 91.7.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-10/
- https://www.mozilla.org/security/advisories/mfsa2022-11/
- https://www.mozilla.org/security/advisories/mfsa2022-12/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1744352
