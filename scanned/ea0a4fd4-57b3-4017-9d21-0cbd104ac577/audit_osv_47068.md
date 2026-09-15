# [C] CVE-2015-8863

## Summary
Severity: Critical
Advisory: CVE-2015-8863
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-06
Source: https://osv.dev/vulnerability/CVE-2015-8863
Type: osv

## Details
Off-by-one error in the tokenadd function in jv_parse.c in jq allows remote attackers to cause a denial of service (crash) via a long JSON-encoded number, which triggers a heap-based buffer overflow.

## References
- http://rhn.redhat.com/errata/RHSA-2016-1098.html
- http://rhn.redhat.com/errata/RHSA-2016-1099.html
- http://rhn.redhat.com/errata/RHSA-2016-1106.html
- https://security.gentoo.org/glsa/201612-20
- https://github.com/stedolan/jq/commit/8eb1367ca44e772963e704a700ef72ae2e12babd
- https://github.com/stedolan/jq/issues/995
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00012.html
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00014.html
- http://www.openwall.com/lists/oss-security/2016/04/23/1
- http://www.openwall.com/lists/oss-security/2016/04/23/2
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=802231
