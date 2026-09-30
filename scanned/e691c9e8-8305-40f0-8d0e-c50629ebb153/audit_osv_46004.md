# [M] In GnuPG through 2.4.8, if a signed message has `\f` at the end of a plaintext line, an adversary...

## Summary
Severity: Medium
Advisory: JLSEC-2026-562
Ecosystem: Julia
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/JLSEC-2026-562
Type: osv

## Affected
- Julia: `GnuPG_jll` — affected >=0 <2.5.16+0

## Details
In GnuPG through 2.4.8, if a signed message has `\f` at the end of a plaintext line, an adversary can construct a modified message that places additional text after the signed material, such that signature verification of the modified message succeeds (although an "invalid armor" message is printed during verification). This is related to use of `\f` as a marker to denote truncation of a long plaintext line.

## References
- https://github.com/advisories/GHSA-w789-3q45-984r
- https://gpg.fail/formfeed
- https://media.ccc.de/v/39c3-to-sign-or-not-to-sign-practical-vulnerabilities-i
- https://news.ycombinator.com/item?id=46404339
- https://nvd.nist.gov/vuln/detail/CVE-2025-68972
