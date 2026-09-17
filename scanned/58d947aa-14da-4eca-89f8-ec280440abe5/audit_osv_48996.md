# [H] CVE-2018-19966

## Summary
Severity: High
Advisory: CVE-2018-19966
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-12-08
Source: https://osv.dev/vulnerability/CVE-2018-19966
Type: osv

## Details
An issue was discovered in Xen through 4.11.x allowing x86 PV guest OS users to cause a denial of service (host OS crash) or possibly gain host OS privileges because of an interpretation conflict for a union data structure associated with shadow paging. NOTE: this issue exists because of an incorrect fix for CVE-2017-15595.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00072.html
- https://lists.debian.org/debian-lts-announce/2019/10/msg00008.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UXC6BME7SXJI2ZIATNXCAH7RGPI4UKTT/
- http://www.securityfocus.com/bid/106182
- https://www.debian.org/security/2019/dsa-4369
- https://xenbits.xen.org/xsa/advisory-280.html
