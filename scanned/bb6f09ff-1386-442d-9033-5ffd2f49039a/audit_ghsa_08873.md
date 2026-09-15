# [H] libcrux: Potential Panic on Overlong Ciphertext Buffer

## Summary
Severity: High
Advisory: GHSA-hc3c-63hc-2r9f
CWE: CWE-120
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-hc3c-63hc-2r9f
Type: github-advisory

## Affected
- crates.io: `libcrux-chacha20poly1305` — affected >=0 <0.0.8

## Details
An application that passes in a ciphertext buffer of length greater
than `ptxt.len() + TAG_LEN` to `libcrux_chacha20poly1305::encrypt` or
`libcrux_chacha20poly1305::xchacha20_poly1305::encrypt` would
experience a panic.

## Impact
An application where the length of the ciphertext buffer is under
attacker control could be made to crash.

## Mitigation
The fix makes it so that `libcrux_chacha20poly1305::encrypt` and
`libcrux_chacha20poly1305::xchacha20_poly1305::encrypt` no longer
panic in this case, but instead write out the ciphertext and tag into
the first `ptxt.len() + TAG_LEN` bytes of the provided buffer.

## References
- https://github.com/cryspen/libcrux/pull/1386
- https://github.com/cryspen/libcrux
- https://rustsec.org/advisories/RUSTSEC-2026-0124.html
