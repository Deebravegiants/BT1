# [H] ALPINE-CVE-2026-59856

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-59856
Ecosystem: Alpine:v3.23
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-59856
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0854-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0736, the PHP omni-completion script in runtime/autoload/phpcomplete.vim interpolates a class or trait name, taken from the contents of the edited buffer, into a search() pattern that is run via win_execute() without escaping. A name containing a single quote can terminate the search() string argument early, and because the bar is honored as an Ex command separator, the remainder of the name is run as Ex commands; via the :! command this allows arbitrary operating-system command execution when a victim opens a crafted PHP file and invokes omni-completion. This issue is fixed in version 9.2.0736.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-59856
