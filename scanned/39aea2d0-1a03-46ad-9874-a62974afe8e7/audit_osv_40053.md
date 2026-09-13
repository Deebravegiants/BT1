# [H] App::Ack versions through 3.10.0 for Perl print unsanitised terminal escape sequences from filenames in several output modes

## Summary
Severity: High
Advisory: CVE-2026-49147
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-49147
Type: osv

## Details
App::Ack versions through 3.10.0 for Perl print unsanitised terminal escape sequences from filenames in several output modes.

When ack prints a filename whose basename contains terminal control bytes such as ANSI escape sequences, those bytes reach the terminal unchanged. Version 3.10.0 added a _safe_filename helper that sanitises the filenames printed by -f, -g, the colored match heading, and per-match lines, but the --show-types, -l/-L, and -c paths still emit the raw filename.

A file whose name embeds cursor-movement or color escapes can overwrite or recolor earlier terminal output, or be passed unchanged to a downstream consumer.

## References
- http://www.openwall.com/lists/oss-security/2026/07/08/9
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49147.json
- https://metacpan.org/release/PETDANCE/ack-v3.10.0/source/Changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-49147
- https://github.com/beyondgrep/ack3
