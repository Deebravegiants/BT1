# [H] CVE-2016-2175

## Summary
Severity: High
Advisory: CVE-2016-2175
Aliases: GHSA-4c32-xmgj-2g98
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-06-01
Source: https://osv.dev/vulnerability/CVE-2016-2175
Type: osv

## Details
Apache PDFBox before 1.8.12 and 2.x before 2.0.1 does not properly initialize the XML parsers, which allows context-dependent attackers to conduct XML External Entity (XXE) attacks via a crafted PDF.

## References
- http://mail-archives.us.apache.org/mod_mbox/www-announce/201605.mbox/%3C83a03bcf-f86b-4688-37b5-615c080291d8%40apache.org%3E
- http://packetstormsecurity.com/files/137214/Apache-PDFBox-1.8.11-2.0.0-XML-Injection.html
- http://www.securityfocus.com/archive/1/538503/100/0/threaded
- http://www.securityfocus.com/bid/90902
- https://lists.apache.org/thread.html/ad5fbc86c1d1821ae1b963e8561ab6d6a5f66b2848e84f5a31477f54%40%3Ccommits.tika.apache.org%3E
- http://rhn.redhat.com/errata/RHSA-2017-0179.html
- http://rhn.redhat.com/errata/RHSA-2017-0248.html
- http://rhn.redhat.com/errata/RHSA-2017-0249.html
- http://rhn.redhat.com/errata/RHSA-2017-0272.html
- http://www.debian.org/security/2016/dsa-3606
- http://svn.apache.org/viewvc?view=revision&revision=1739564
- http://svn.apache.org/viewvc?view=revision&revision=1739565
