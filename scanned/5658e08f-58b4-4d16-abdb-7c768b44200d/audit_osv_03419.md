# [H] ALPINE-CVE-2026-11527

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-11527
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-06-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-11527
Type: osv

## Affected
- Alpine:v3.21: `perl-config-inifiles` — affected >=0 <3.002000-r0
- Alpine:v3.22: `perl-config-inifiles` — affected >=0 <3.002000-r0
- Alpine:v3.23: `perl-config-inifiles` — affected >=0 <3.002000-r0
- Alpine:v3.24: `perl-config-inifiles` — affected >=0 <3.002000-r0

## Details
Config::IniFiles versions before 3.001000 for Perl allow OS command injection and file overwrite via a 2-arg open() of the -file argument in _make_filehandle.

Config::IniFiles::_make_filehandle opens a filename argument with Perl's 2-arg open(), so a filename that begins or ends with a pipe ("| cmd", "cmd |") or begins with a redirect ("> path", ">> path") is run as a command or redirect rather than opened as a file. The helper is the open path behind the documented -file argument: new(-file => $thing) reaches it through ReadConfig. An in-memory scalar reference (-file => \$text) does not open a path and is unaffected.

Any caller that forwards untrusted input to the -file argument can run an arbitrary command or truncate a file under the process UID.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-11527
