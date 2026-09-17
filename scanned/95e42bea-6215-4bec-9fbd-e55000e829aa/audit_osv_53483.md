# [H] CVE-2022-45409

## Summary
Severity: High
Advisory: CVE-2022-45409
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-45409
Type: osv

## Details
The garbage collector could have been aborted in several states and zones and <code>GCRuntime::finishCollection</code> may not have been called, leading to a use-after-free and potentially exploitable crash. This vulnerability affects Firefox ESR < 102.5, Thunderbird < 102.5, and Firefox < 107.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-47/
- https://www.mozilla.org/security/advisories/mfsa2022-48/
- https://www.mozilla.org/security/advisories/mfsa2022-49/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1796901
