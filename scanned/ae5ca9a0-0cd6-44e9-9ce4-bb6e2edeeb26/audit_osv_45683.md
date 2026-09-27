# [H] JLSEC-2026-20

## Summary
Severity: High
Advisory: JLSEC-2026-20
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/JLSEC-2026-20
Type: osv

## Affected
- Julia: `hyper_jll` — affected >=0 <0.14.19+0

## Details
Hyperium Hyper before 0.14.19 does not allow for customization of the `max_header_list_size` method in the H2 third-party software, allowing attackers to perform HTTP2 attacks.

## References
- https://github.com/hyperium/hyper/compare/v0.14.18...v0.14.19
- https://github.com/hyperium/hyper/issues/2826
- https://github.com/hyperium/hyper/pull/2828
