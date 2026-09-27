# [C] ALPINE-CVE-2026-11526

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-11526
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-11526
Type: osv

## Affected
- Alpine:v3.21: `perl-gd` — affected >=0 <2.86-r0
- Alpine:v3.22: `perl-gd` — affected >=0 <2.86-r0
- Alpine:v3.23: `perl-gd` — affected >=0 <2.86-r0
- Alpine:v3.24: `perl-gd` — affected >=0 <2.86-r0

## Details
GD versions before 2.86 for Perl allow OS command injection and file overwrite via a 2-arg open() of filename arguments in _make_filehandle.

GD::Image::_make_filehandle opens a filename argument with Perl's 2-arg open(), so a filename that begins or ends with a pipe ("| cmd", "cmd |") or begins with a redirect ("> path", ">> path") is run as a command or redirect rather than opened as a file. _make_filehandle is the single open path behind every filename-accepting constructor (new, newFromPng, newFromJpeg, and the rest); the in-memory *Data variants do not open a path and are unaffected.

Any caller that forwards untrusted input to one of these constructors as a pathname can run an arbitrary command or truncate a file under the process UID.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-11526
