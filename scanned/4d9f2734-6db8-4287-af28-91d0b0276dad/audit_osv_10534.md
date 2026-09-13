# [H] CVE-2017-16882

## Summary
Severity: High
Advisory: CVE-2017-16882
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-18
Source: https://osv.dev/vulnerability/CVE-2017-16882
Type: osv

## Details
Icinga Core through 1.14.0 initially executes bin/icinga as root but supports configuration options in which this file is owned by a non-root account (and similarly can have etc/icinga.cfg owned by a non-root account), which allows local users to gain privileges by leveraging access to this non-root account, a related issue to CVE-2017-14312. This also affects bin/icingastats, bin/ido2db, and bin/log2ido.

## References
- https://github.com/Icinga/icinga-core/issues/1601
- https://security.gentoo.org/glsa/202007-31
