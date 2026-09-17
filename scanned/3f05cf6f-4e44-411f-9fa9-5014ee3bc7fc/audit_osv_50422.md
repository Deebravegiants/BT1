# [H] CVE-2020-15685

## Summary
Severity: High
Advisory: CVE-2020-15685
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2020-15685
Type: osv

## Details
During the plaintext phase of the STARTTLS connection setup, protocol commands could have been injected and evaluated within the encrypted session. This vulnerability affects Thunderbird < 78.7.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-05/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1622640
