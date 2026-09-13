# [M] CVE-2018-19965

## Summary
Severity: Medium
Advisory: CVE-2018-19965
CVSS: 5.6 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-12-08
Source: https://osv.dev/vulnerability/CVE-2018-19965
Type: osv

## Details
An issue was discovered in Xen through 4.11.x allowing 64-bit PV guest OS users to cause a denial of service (host OS crash) because #GP[0] can occur after a non-canonical address is passed to the TLB flushing code. NOTE: this issue exists because of an incorrect CVE-2017-5754 (aka Meltdown) mitigation.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00072.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UXC6BME7SXJI2ZIATNXCAH7RGPI4UKTT/
- http://www.securityfocus.com/bid/106182
- https://www.debian.org/security/2019/dsa-4369
- https://support.citrix.com/article/CTX239432
- https://xenbits.xen.org/xsa/advisory-279.html
