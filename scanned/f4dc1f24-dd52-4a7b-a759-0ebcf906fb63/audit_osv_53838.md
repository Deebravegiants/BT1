# [H] CVE-2023-28162

## Summary
Severity: High
Advisory: CVE-2023-28162
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-28162
Type: osv

## Details
While implementing AudioWorklets, some code may have casted one type to another, invalid, dynamic type. This could have led to a potentially exploitable crash. This vulnerability affects Firefox < 111, Firefox ESR < 102.9, and Thunderbird < 102.9.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-09/
- https://www.mozilla.org/security/advisories/mfsa2023-10/
- https://www.mozilla.org/security/advisories/mfsa2023-11/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1811327
