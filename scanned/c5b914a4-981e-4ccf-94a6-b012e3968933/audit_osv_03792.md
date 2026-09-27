# [H] ALPINE-CVE-2026-49147

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-49147
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-49147
Type: osv

## Affected
- Alpine:v3.24: `ack` — affected >=0 <3.10.0-r0

## Details
App::Ack versions through 3.10.0 for Perl print unsanitised terminal escape sequences from filenames in several output modes.

When ack prints a filename whose basename contains terminal control bytes such as ANSI escape sequences, those bytes reach the terminal unchanged. Version 3.10.0 added a _safe_filename helper that sanitises the filenames printed by -f, -g, the colored match heading, and per-match lines, but the --show-types, -l/-L, and -c paths still emit the raw filename.

A file whose name embeds cursor-movement or color escapes can overwrite or recolor earlier terminal output, or be passed unchanged to a downstream consumer.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-49147
