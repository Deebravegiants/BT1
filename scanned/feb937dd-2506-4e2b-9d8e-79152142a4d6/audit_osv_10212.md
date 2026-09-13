# [H] CVE-2017-14312

## Summary
Severity: High
Advisory: CVE-2017-14312
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-11
Source: https://osv.dev/vulnerability/CVE-2017-14312
Type: osv

## Details
Nagios Core through 4.3.4 initially executes /usr/sbin/nagios as root but supports configuration options in which this file is owned by a non-root account (and similarly can have nagios.cfg owned by a non-root account), which allows local users to gain privileges by leveraging access to this non-root account.

## References
- http://www.securityfocus.com/bid/100881
- https://security.gentoo.org/glsa/201812-03
- https://github.com/NagiosEnterprises/nagioscore/issues/424
