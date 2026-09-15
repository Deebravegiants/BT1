# [H] ALPINE-CVE-2026-57077

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-57077
Ecosystem: Alpine:v3.24
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-57077
Type: osv

## Affected
- Alpine:v3.24: `perl-yaml-syck` — affected >=0 <1.47-r0

## Details
YAML::Syck versions before 1.47 for Perl allow an out-of-bounds read via an unbounded newline scan in newline_len.

In the bundled libsyck newline_len and is_newline dereference the scan pointer, and the following byte for a "\r\n" pair, with no NUL-terminator or bounds check. During block-scalar lexing at a document boundary the scan runs one byte past the heap lexer buffer. This is an incomplete fix of CVE-2025-11683, on a lexer path the earlier fix did not cover.

Any caller that runs Load or LoadFile on an untrusted document with a block scalar at a document boundary reaches the over-read.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-57077
