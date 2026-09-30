# [H] ALPINE-CVE-2026-41066

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-41066
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-41066
Type: osv

## Affected
- Alpine:v3.24: `py3-lxml` — affected >=0 <6.1.0-r0

## Details
lxml is a library for processing XML and HTML in the Python language. Prior to 6.1.0, using either of the two parsers in the default configuration (with resolve_entities=True) allows untrusted XML input to read local files. Setting the resolve_entities option explicitly to resolve_entities='internal' or resolve_entities=False disables the local file access. This vulnerability is fixed in 6.1.0.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-41066
