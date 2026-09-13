# [M] CVE-2016-7569

## Summary
Severity: Medium
Advisory: CVE-2016-7569
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/CVE-2016-7569
Type: osv

## Details
Directory traversal vulnerability in docker2aci before 0.13.0 allows remote attackers to write to arbitrary files via a .. (dot dot) in the embedded layer data in an image.

## References
- http://www.securityfocus.com/bid/93194
- http://www.openwall.com/lists/oss-security/2016/09/28/4
- https://github.com/appc/docker2aci/issues/201
- https://github.com/appc/docker2aci/releases/tag/v0.13.0
- http://www.openwall.com/lists/oss-security/2016/09/28/2
