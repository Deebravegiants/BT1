# [H] CVE-2016-10091

## Summary
Severity: High
Advisory: CVE-2016-10091
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-21
Source: https://osv.dev/vulnerability/CVE-2016-10091
Type: osv

## Details
Multiple stack-based buffer overflows in unrtf 0.21.9 allow remote attackers to cause a denial-of-service by writing a negative integer to the (1) cmd_expand function, (2) cmd_emboss function, or (3) cmd_engrave function.

## References
- http://www.openwall.com/lists/oss-security/2016/12/31/3
- http://www.openwall.com/lists/oss-security/2017/01/01/1
- http://www.securityfocus.com/bid/95173
- http://hg.savannah.gnu.org/hgweb/unrtf/rev/3b16893a6406
- https://bugzilla.redhat.com/show_bug.cgi?id=1409546
