# [H] CVE-2008-5183

## Summary
Severity: High
Advisory: CVE-2008-5183
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2008-11-21
Source: https://osv.dev/vulnerability/CVE-2008-5183
Type: osv

## Details
cupsd in CUPS 1.3.9 and earlier allows local users, and possibly remote attackers, to cause a denial of service (daemon crash) by adding a large number of RSS Subscriptions, which triggers a NULL pointer dereference.  NOTE: this issue can be triggered remotely by leveraging CVE-2008-5184.

## References
- http://secunia.com/advisories/33937
- http://secunia.com/advisories/43521
- http://support.apple.com/kb/HT3438
- http://www.debian.org/security/2011/dsa-2176
- http://www.mandriva.com/security/advisories?name=MDVSA-2009:028
- http://www.securityfocus.com/bid/32419
- http://www.securitytracker.com/id?1021396
- http://www.vupen.com/english/advisories/2009/0422
- http://www.vupen.com/english/advisories/2011/0535
- https://exchange.xforce.ibmcloud.com/vulnerabilities/46684
- https://www.exploit-db.com/exploits/7150
- http://lists.apple.com/archives/security-announce/2009/Feb/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2008-11/msg00002.html
- http://www.gnucitizen.org/blog/pwning-ubuntu-via-cups/
- http://www.openwall.com/lists/oss-security/2008/11/19/3
- http://www.openwall.com/lists/oss-security/2008/11/19/4
- http://www.openwall.com/lists/oss-security/2008/11/20/1
- https://bugs.launchpad.net/ubuntu/+source/cups/+bug/298241
- http://lab.gnucitizen.org/projects/cups-0day
- http://www.redhat.com/support/errata/RHSA-2008-1029.html
