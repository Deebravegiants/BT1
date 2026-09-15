# [H] CVE-2023-48183

## Summary
Severity: High
Advisory: CVE-2023-48183
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-23
Source: https://osv.dev/vulnerability/CVE-2023-48183
Type: osv

## Details
QuickJS before c4cdd61 has a build_for_in_iterator NULL pointer dereference because of an erroneous lexical scope of "this" with eval.

## References
- https://github.com/bellard/quickjs/issues/192
- https://github.com/bellard/quickjs/commit/c4cdd61a3ed284cd760faf6b00bbf0cb908da077
