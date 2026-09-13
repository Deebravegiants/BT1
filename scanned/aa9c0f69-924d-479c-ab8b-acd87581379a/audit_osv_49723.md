# [H] CVE-2019-17341

## Summary
Severity: High
Advisory: CVE-2019-17341
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-10-08
Source: https://osv.dev/vulnerability/CVE-2019-17341
Type: osv

## Details
An issue was discovered in Xen through 4.11.x allowing x86 PV guest OS users to cause a denial of service or gain privileges by leveraging a page-writability race condition during addition of a passed-through PCI device.

## References
- https://www.debian.org/security/2020/dsa-4602
- https://xenbits.xen.org/xsa/advisory-285.html
- https://seclists.org/bugtraq/2020/Jan/21
- http://xenbits.xen.org/xsa/advisory-285.html
- http://www.openwall.com/lists/oss-security/2019/10/25/6
