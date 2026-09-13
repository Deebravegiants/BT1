# [H] CVE-2017-16667

## Summary
Severity: High
Advisory: CVE-2017-16667
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-08
Source: https://osv.dev/vulnerability/CVE-2017-16667
Type: osv

## Details
backintime (aka Back in Time) before 1.1.24 did improper escaping/quoting of file paths used as arguments to the 'notify-send' command, leading to some parts of file paths being executed as shell commands within an os.system call in qt4/plugins/notifyplugin.py. This could allow an attacker to craft an unreadable file with a specific name to run arbitrary shell commands.

## References
- https://github.com/bit-team/backintime/issues/834
- https://github.com/bit-team/backintime/releases/tag/v1.1.24
- https://security.gentoo.org/glsa/201801-06
- https://github.com/bit-team/backintime/commit/cef81d0da93ff601252607df3db1a48f7f6f01b3
