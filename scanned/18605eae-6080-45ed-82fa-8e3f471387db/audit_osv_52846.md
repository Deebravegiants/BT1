# [H] CVE-2022-1802

## Summary
Severity: High
Advisory: CVE-2022-1802
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-1802
Type: osv

## Details
If an attacker was able to corrupt the methods of an Array object in JavaScript via prototype pollution, they could have achieved execution of attacker-controlled JavaScript code in a privileged context. This vulnerability affects Firefox ESR < 91.9.1, Firefox < 100.0.2, Firefox for Android < 100.3.0, and Thunderbird < 91.9.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-19/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1770137
