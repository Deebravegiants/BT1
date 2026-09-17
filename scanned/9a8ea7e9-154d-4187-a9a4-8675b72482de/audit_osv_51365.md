# [M] CVE-2021-29956

## Summary
Severity: Medium
Advisory: CVE-2021-29956
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2021-06-24
Source: https://osv.dev/vulnerability/CVE-2021-29956
Type: osv

## Details
OpenPGP secret keys that were imported using Thunderbird version 78.8.1 up to version 78.10.1 were stored unencrypted on the user's local disk. The master password protection was inactive for those keys. Version 78.10.2 will restore the protection mechanism for newly imported keys, and will automatically protect keys that had been imported using affected Thunderbird versions. This vulnerability affects Thunderbird < 78.10.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-22/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1710290
