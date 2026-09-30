# [H] CVE-2022-38476

## Summary
Severity: High
Advisory: CVE-2022-38476
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-38476
Type: osv

## Details
A data race could occur in the <code>PK11_ChangePW</code> function, potentially leading to a use-after-free vulnerability. In Firefox, this lock protected the data when a user changed their master password. This vulnerability affects Firefox ESR < 102.2 and Thunderbird < 102.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-34/
- https://www.mozilla.org/security/advisories/mfsa2022-36/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1760998
