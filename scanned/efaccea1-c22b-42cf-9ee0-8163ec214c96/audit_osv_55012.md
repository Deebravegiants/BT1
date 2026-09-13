# [C] CVE-2024-8385

## Summary
Severity: Critical
Advisory: CVE-2024-8385
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-03
Source: https://osv.dev/vulnerability/CVE-2024-8385
Type: osv

## Details
A difference in the handling of StructFields and ArrayTypes in WASM could be used to trigger an exploitable type confusion vulnerability. This vulnerability affects Firefox < 130, Firefox ESR < 128.2, and Thunderbird < 128.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-43/
- https://www.mozilla.org/security/advisories/mfsa2024-39/
- https://www.mozilla.org/security/advisories/mfsa2024-40/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1911909
