# [H] CVE-2022-1529

## Summary
Severity: High
Advisory: CVE-2022-1529
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-1529
Type: osv

## Details
An attacker could have sent a message to the parent process where the contents were used to double-index into a JavaScript object, leading to prototype pollution and ultimately attacker-controlled JavaScript executing in the privileged parent process. This vulnerability affects Firefox ESR < 91.9.1, Firefox < 100.0.2, Firefox for Android < 100.3.0, and Thunderbird < 91.9.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-19/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1770048
