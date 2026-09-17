# [H] CVE-2023-25729

## Summary
Severity: High
Advisory: CVE-2023-25729
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-25729
Type: osv

## Details
Permission prompts for opening external schemes were only shown for <code>ContentPrincipals</code> resulting in extensions being able to open them without user interaction via <code>ExpandedPrincipals</code>. This could lead to further malicious actions such as downloading files or interacting with software already installed on the system. This vulnerability affects Firefox < 110, Thunderbird < 102.8, and Firefox ESR < 102.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-05/
- https://www.mozilla.org/security/advisories/mfsa2023-06/
- https://www.mozilla.org/security/advisories/mfsa2023-07/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1792138
