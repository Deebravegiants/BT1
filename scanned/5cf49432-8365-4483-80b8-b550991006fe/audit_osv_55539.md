# [M] CVE-2025-68972

## Summary
Severity: Medium
Advisory: CVE-2025-68972
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-12-27
Source: https://osv.dev/vulnerability/CVE-2025-68972
Type: osv

## Details
In GnuPG through 2.4.8, if a signed message has \f at the end of a plaintext line, an adversary can construct a modified message that places additional text after the signed material, such that signature verification of the modified message succeeds (although an "invalid armor" message is printed during verification). This is related to use of \f as a marker to denote truncation of a long plaintext line.

## References
- https://gpg.fail/formfeed
- https://media.ccc.de/v/39c3-to-sign-or-not-to-sign-practical-vulnerabilities-i
- https://news.ycombinator.com/item?id=46404339
