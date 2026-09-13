# [H] CVE-2023-25739

## Summary
Severity: High
Advisory: CVE-2023-25739
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-25739
Type: osv

## Details
Module load requests that failed were not being checked as to whether or not they were cancelled causing a use-after-free in <code>ScriptLoadContext</code>. This vulnerability affects Firefox < 110, Thunderbird < 102.8, and Firefox ESR < 102.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-06/
- https://www.mozilla.org/security/advisories/mfsa2023-07/
- https://www.mozilla.org/security/advisories/mfsa2023-05/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1811939
