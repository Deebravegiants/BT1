# [H] ALPINE-CVE-2026-49145

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-49145
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-49145
Type: osv

## Affected
- Alpine:v3.24: `ack` — affected >=0 <3.10.0-r0

## Details
App::Ack versions through 3.10.0 for Perl read arbitrary files via --files-from in a project .ackrc.

ack searches up the directory hierarchy from the current directory for a project .ackrc and loads its options. The project-source option blocklist in App::Ack::ConfigLoader does not include --files-from, so a project .ackrc can set it to a path whose listed files ack then reads and searches. Version 3.10.0 added --follow to the blocklist; --files-from remains accepted.

A project .ackrc committed to an untrusted repository can make ack read files outside the project and print their matching lines.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-49145
