# [H] CVE-2013-4508

## Summary
Severity: High
Advisory: CVE-2013-4508
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2013-11-08
Source: https://osv.dev/vulnerability/CVE-2013-4508
Type: osv

## Details
lighttpd before 1.4.34, when SNI is enabled, configures weak SSL ciphers, which makes it easier for remote attackers to hijack sessions by inserting packets into the client-server data stream or obtain sensitive information by sniffing the network.

## References
- http://download.lighttpd.net/lighttpd/security/lighttpd_sa_2013_01.txt
- http://jvn.jp/en/jp/JVN37417423/index.html
- http://lists.opensuse.org/opensuse-updates/2014-01/msg00049.html
- http://marc.info/?l=bugtraq&m=141576815022399&w=2
- http://openwall.com/lists/oss-security/2013/11/04/19
- http://redmine.lighttpd.net/issues/2525
- https://www.debian.org/security/2013/dsa-2795
- http://lists.opensuse.org/opensuse-updates/2014-01/msg00049.html
- http://openwall.com/lists/oss-security/2013/11/04/19
- http://download.lighttpd.net/lighttpd/security/lighttpd_sa_2013_01.txt
- http://marc.info/?l=bugtraq&m=141576815022399&w=2
- http://redmine.lighttpd.net/issues/2525
- http://download.lighttpd.net/lighttpd/security/lighttpd_sa_2013_01.txt
- http://redmine.lighttpd.net/projects/lighttpd/repository/revisions/2913/diff/
