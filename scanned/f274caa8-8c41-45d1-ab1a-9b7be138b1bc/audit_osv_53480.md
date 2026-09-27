# [M] CVE-2022-45405

## Summary
Severity: Medium
Advisory: CVE-2022-45405
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-45405
Type: osv

## Details
Freeing arbitrary <code>nsIInputStream</code>'s on a different thread than creation could have led to a use-after-free and potentially exploitable crash. This vulnerability affects Firefox ESR < 102.5, Thunderbird < 102.5, and Firefox < 107.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-47/
- https://www.mozilla.org/security/advisories/mfsa2022-48/
- https://www.mozilla.org/security/advisories/mfsa2022-49/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1791314
