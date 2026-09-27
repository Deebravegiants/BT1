# [H] CVE-2010-0013

## Summary
Severity: High
Advisory: CVE-2010-0013
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2010-01-09
Source: https://osv.dev/vulnerability/CVE-2010-0013
Type: osv

## Details
Directory traversal vulnerability in slp.c in the MSN protocol plugin in libpurple in Pidgin 2.6.4 and Adium 1.3.8 allows remote attackers to read arbitrary files via a .. (dot dot) in an application/x-msnmsgrp2p MSN emoticon (aka custom smiley) request, a related issue to CVE-2004-0122.  NOTE: it could be argued that this is resultant from a vulnerability in which an emoticon download request is processed even without a preceding text/x-mms-emoticon message that announced availability of the emoticon.

## References
- http://secunia.com/advisories/37953
- http://secunia.com/advisories/37954
- http://secunia.com/advisories/37961
- http://secunia.com/advisories/38915
- http://www.mandriva.com/security/advisories?name=MDVSA-2010:085
- http://www.vupen.com/english/advisories/2009/3662
- http://www.vupen.com/english/advisories/2009/3663
- http://lists.fedoraproject.org/pipermail/package-announce/2010-January/033771.html
- http://lists.fedoraproject.org/pipermail/package-announce/2010-January/033848.html
- http://lists.opensuse.org/opensuse-security-announce/2010-03/msg00004.html
- http://www.openwall.com/lists/oss-security/2010/01/02/1
- http://www.openwall.com/lists/oss-security/2010/01/07/1
- http://www.openwall.com/lists/oss-security/2010/01/07/2
- http://www.openwall.com/lists/oss-security/2010/01/02/1
- https://bugzilla.redhat.com/show_bug.cgi?id=552483
- http://www.vupen.com/english/advisories/2009/3662
- http://www.vupen.com/english/advisories/2009/3663
- http://www.vupen.com/english/advisories/2010/1020
- https://bugzilla.redhat.com/show_bug.cgi?id=552483
- http://d.pidgin.im/viewmtn/revision/info/3d02401cf232459fc80c0837d31e05fae7ae5467
