# [H] CVE-2019-17342

## Summary
Severity: High
Advisory: CVE-2019-17342
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-08
Source: https://osv.dev/vulnerability/CVE-2019-17342
Type: osv

## Details
An issue was discovered in Xen through 4.11.x allowing x86 PV guest OS users to cause a denial of service or gain privileges by leveraging a race condition that arose when XENMEM_exchange was introduced.

## References
- https://seclists.org/bugtraq/2020/Jan/21
- https://www.debian.org/security/2020/dsa-4602
- https://xenbits.xen.org/xsa/advisory-287.html
- http://xenbits.xen.org/xsa/advisory-287.html
- http://www.openwall.com/lists/oss-security/2019/10/25/2
