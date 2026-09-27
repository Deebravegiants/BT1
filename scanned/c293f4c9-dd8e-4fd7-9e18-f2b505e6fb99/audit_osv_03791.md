# [H] ALPINE-CVE-2026-49146

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-49146
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-49146
Type: osv

## Affected
- Alpine:v3.24: `ack` — affected >=0 <3.10.0-r0

## Details
App::Ack versions before 3.10.0 for Perl allow memory exhaustion via an unbounded context value in a project .ackrc.

ack searches up the directory hierarchy from the current directory for a project .ackrc and loads its options. The -B and -C context options accepted any positive integer, and ack sized the before-context buffer to that value, so a project .ackrc setting --before-context=100000000 made ack allocate a buffer of 100 million elements.

A project .ackrc committed to an untrusted repository can abort ack with an out-of-memory condition.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-49146
