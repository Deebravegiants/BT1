# [H] CVE-2021-29950

## Summary
Severity: High
Advisory: CVE-2021-29950
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-24
Source: https://osv.dev/vulnerability/CVE-2021-29950
Type: osv

## Details
Thunderbird unprotects a secret OpenPGP key prior to using it for a decryption, signing or key import task. If the task runs into a failure, the secret key may remain in memory in its unprotected state. This vulnerability affects Thunderbird < 78.8.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-17/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1673239
