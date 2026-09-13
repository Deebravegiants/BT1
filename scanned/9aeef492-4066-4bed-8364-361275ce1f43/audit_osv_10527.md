# [H] CVE-2017-16834

## Summary
Severity: High
Advisory: CVE-2017-16834
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-16
Source: https://osv.dev/vulnerability/CVE-2017-16834
Type: osv

## Details
PNP4Nagios through 0.6.26 has /usr/bin/npcd and npcd.cfg owned by an unprivileged account but root code execution depends on these files, which allows local users to gain privileges by leveraging access to this unprivileged account.

## References
- https://security.gentoo.org/glsa/201806-09
- https://github.com/lingej/pnp4nagios/issues/140
