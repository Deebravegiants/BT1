# [H] CVE-2014-0224

## Summary
Severity: High
Advisory: CVE-2014-0224
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2014-06-05
Source: https://osv.dev/vulnerability/CVE-2014-0224
Type: osv

## Details
OpenSSL before 0.9.8za, 1.0.0 before 1.0.0m, and 1.0.1 before 1.0.1h does not properly restrict processing of ChangeCipherSpec messages, which allows man-in-the-middle attackers to trigger use of a zero-length master key in certain OpenSSL-to-OpenSSL communications, and consequently hijack sessions or obtain sensitive information, via a crafted TLS handshake, aka the "CCS Injection" vulnerability.

## References
- http://aix.software.ibm.com/aix/efixes/security/openssl_advisory9.asc
- http://ccsinjection.lepidum.co.jp
- http://dev.mysql.com/doc/relnotes/workbench/en/wb-news-6-1-7.html
- http://esupport.trendmicro.com/solution/en-US/1103813.aspx
- http://kb.juniper.net/InfoCenter/index?page=content&id=KB29217
- http://linux.oracle.com/errata/ELSA-2014-1053.html
- http://lists.fedoraproject.org/pipermail/package-announce/2014-August/136470.html
- http://lists.fedoraproject.org/pipermail/package-announce/2014-August/136473.html
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2015-04/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00011.html
- http://lists.opensuse.org/opensuse-updates/2015-02/msg00030.html
- http://marc.info/?l=bugtraq&m=140266410314613&w=2
- http://marc.info/?l=bugtraq&m=140317760000786&w=2
- http://marc.info/?l=bugtraq&m=140369637402535&w=2
- http://marc.info/?l=bugtraq&m=140386311427810&w=2
- http://marc.info/?l=bugtraq&m=140389274407904&w=2
- http://marc.info/?l=bugtraq&m=140389355508263&w=2
- http://marc.info/?l=bugtraq&m=140431828824371&w=2
- http://marc.info/?l=bugtraq&m=140448122410568&w=2
