# [C] CVE-2022-26486

## Summary
Severity: Critical
Advisory: CVE-2022-26486
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-26486
Type: osv

## Details
An unexpected message in the WebGPU IPC framework could lead to a use-after-free and exploitable sandbox escape. We have had reports of attacks in the wild abusing this flaw. This vulnerability affects Firefox < 97.0.2, Firefox ESR < 91.6.1, Firefox for Android < 97.3.0, Thunderbird < 91.6.2, and Focus < 97.3.0.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-26486
- https://bugzilla.mozilla.org/show_bug.cgi?id=1758070
- https://www.mozilla.org/security/advisories/mfsa2022-09/
