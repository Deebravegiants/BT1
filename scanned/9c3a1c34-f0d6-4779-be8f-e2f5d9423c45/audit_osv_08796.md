# [H] CVE-2016-6173

## Summary
Severity: High
Advisory: CVE-2016-6173
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/CVE-2016-6173
Type: osv

## Details
NSD before 4.1.11 allows remote DNS master servers to cause a denial of service (/tmp disk consumption and slave server crash) via a zone transfer with unlimited data.

## References
- http://www.nlnetlabs.nl/svn/nsd/tags/NSD_4_1_11_REL/doc/RELNOTES
- http://www.openwall.com/lists/oss-security/2016/07/06/3
- http://www.openwall.com/lists/oss-security/2016/07/06/4
- http://www.securityfocus.com/bid/91678
- https://github.com/sischkg/xfer-limit/blob/master/README.md
- https://lists.dns-oarc.net/pipermail/dns-operations/2016-July/015058.html
- https://open.nlnetlabs.nl/pipermail/nsd-users/2016-August/002342.html
- https://www.nlnetlabs.nl/bugs-script/show_bug.cgi?id=790
