# [C] CVE-2016-7406

## Summary
Severity: Critical
Advisory: CVE-2016-7406
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-03
Source: https://osv.dev/vulnerability/CVE-2016-7406
Type: osv

## Details
Format string vulnerability in Dropbear SSH before 2016.74 allows remote attackers to execute arbitrary code via format string specifiers in the (1) username or (2) host argument.

## References
- http://seclists.org/fulldisclosure/2024/Aug/35
- http://www.securityfocus.com/bid/92974
- https://bugzilla.redhat.com/show_bug.cgi?id=1376353
- http://www.openwall.com/lists/oss-security/2016/09/15/2
- https://secure.ucc.asn.au/hg/dropbear/rev/b66a483f3dcb
- https://security.gentoo.org/glsa/201702-23
