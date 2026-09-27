# [H] CVE-2022-2200

## Summary
Severity: High
Advisory: CVE-2022-2200
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-2200
Type: osv

## Details
If an object prototype was corrupted by an attacker, they would have been able to set undesired attributes on a JavaScript object, leading to privileged code execution. This vulnerability affects Firefox < 102, Firefox ESR < 91.11, Thunderbird < 102, and Thunderbird < 91.11.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-24/
- https://www.mozilla.org/security/advisories/mfsa2022-25/
- https://www.mozilla.org/security/advisories/mfsa2022-26/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1771381
