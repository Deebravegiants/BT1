# [M] ALPINE-CVE-2026-13593

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-13593
Ecosystem: Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-13593
Type: osv

## Affected
- Alpine:v3.24: `perl-css-minifier-xs` — affected >=0 <0.16-r0

## Details
CSS::Minifier::XS versions before 0.14 for Perl have a memory leak when the entire document is minified away.

The minify function has a memory leak when processing a document containing only characters to be removed, such as comments and whitespace.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-13593
