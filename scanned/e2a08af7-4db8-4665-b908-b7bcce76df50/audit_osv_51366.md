# [M] CVE-2021-29957

## Summary
Severity: Medium
Advisory: CVE-2021-29957
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2021-06-24
Source: https://osv.dev/vulnerability/CVE-2021-29957
Type: osv

## Details
If a MIME encoded email contains an OpenPGP inline signed or encrypted message part, but also contains an additional unprotected part, Thunderbird did not indicate that only parts of the message are protected. This vulnerability affects Thunderbird < 78.10.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-22/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1673241
