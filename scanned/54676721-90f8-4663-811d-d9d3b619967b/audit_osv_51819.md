# [M] CVE-2021-4126

## Summary
Severity: Medium
Advisory: CVE-2021-4126
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2021-4126
Type: osv

## Details
When receiving an OpenPGP/MIME signed email message that contains an additional outer MIME message layer, for example a message footer added by a mailing list gateway, Thunderbird only considered the inner signed message for the signature validity. This gave the false impression that the additional contents were also covered by the digital signature. Starting with Thunderbird version 91.4.1, only the signature that belongs to the top level MIME part will be considered for the displayed status. This vulnerability affects Thunderbird < 91.4.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-55/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1732310
