# [M] ALPINE-CVE-2026-56016

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-56016
Ecosystem: Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-56016
Type: osv

## Affected
- Alpine:v3.24: `perl-cgi-session` — affected >=0 <4.49-r0

## Details
CGI::Session::ID::md5 versions before 4.49 for Perl generate predictable session ids from low-entropy sources.

The generate_id method builds the session id from a MD5 digest of the process id, the epoch time, and the built-in rand() function. All three are predictable, low-entropy sources: the PID is drawn from a small range, the epoch time can be guessed or read from the HTTP Date header, and Perl's rand() is unsuitable for security purposes because it is predictable and reversible.

An attacker who predicts a session id can impersonate the corresponding session and bypass authentication.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-56016
