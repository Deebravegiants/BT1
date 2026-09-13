# [M] CVE-2019-20384

## Summary
Severity: Medium
Advisory: CVE-2019-20384
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-01-21
Source: https://osv.dev/vulnerability/CVE-2019-20384
Type: osv

## Details
Gentoo Portage through 2.3.84 allows local users to place a Trojan horse plugin in the /usr/lib64/nagios/plugins directory by leveraging access to the nagios user account, because this directory is writable in between a call to emake and a call to fowners.

## References
- https://bugs.gentoo.org/692492
- http://www.openwall.com/lists/oss-security/2020/01/21/1
