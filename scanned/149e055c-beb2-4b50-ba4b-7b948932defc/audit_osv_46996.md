# [C] CVE-2015-8710

## Summary
Severity: Critical
Advisory: CVE-2015-8710
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-11
Source: https://osv.dev/vulnerability/CVE-2015-8710
Type: osv

## Details
The htmlParseComment function in HTMLparser.c in libxml2 allows attackers to obtain sensitive information, cause a denial of service (out-of-bounds heap memory access and application crash), or possibly have unspecified other impact via an unclosed HTML comment.

## References
- http://rhn.redhat.com/errata/RHSA-2016-1089.html
- http://www.debian.org/security/2015/dsa-3430
- http://www.securityfocus.com/bid/79811
- https://git.gnome.org/browse/libxml2/commit/?id=e724879d964d774df9b7969fc846605aa1bac54c
- https://hackerone.com/reports/57125#activity-384861
- http://www.openwall.com/lists/oss-security/2015/04/19/4
- http://www.openwall.com/lists/oss-security/2015/09/13/1
- http://www.openwall.com/lists/oss-security/2015/12/31/7
- http://www.openwall.com/lists/oss-security/2015/04/19/4
- https://bugzilla.gnome.org/show_bug.cgi?id=746048
