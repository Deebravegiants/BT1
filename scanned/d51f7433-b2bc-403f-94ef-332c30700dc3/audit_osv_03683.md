# [C] ALPINE-CVE-2026-4177

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-4177
Ecosystem: Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-03-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-4177
Type: osv

## Affected
- Alpine:v3.24: `perl-yaml-syck` — affected >=0 <1.45-r0

## Details
YAML::Syck versions through 1.36 for Perl has several potential security vulnerabilities including a high-severity heap buffer overflow in the YAML emitter.

The heap overflow occurs when class names exceed the initial 512-byte allocation.

The base64 decoder could read past the buffer end on trailing newlines.

strtok mutated n->type_id in place, corrupting shared node data.

A memory leak occurred in syck_hdlr_add_anchor when a node already had an anchor. The incoming anchor string 'a' was leaked on early return.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-4177
