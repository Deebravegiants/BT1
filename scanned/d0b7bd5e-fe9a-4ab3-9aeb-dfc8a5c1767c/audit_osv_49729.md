# [H] CVE-2019-17347

## Summary
Severity: High
Advisory: CVE-2019-17347
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-08
Source: https://osv.dev/vulnerability/CVE-2019-17347
Type: osv

## Details
An issue was discovered in Xen through 4.11.x allowing x86 PV guest OS users to cause a denial of service or gain privileges because a guest can manipulate its virtualised %cr4 in a way that is incompatible with Linux (and possibly other guest kernels).

## References
- https://seclists.org/bugtraq/2020/Jan/21
- https://www.debian.org/security/2020/dsa-4602
- https://xenbits.xen.org/xsa/advisory-293.html
- http://xenbits.xen.org/xsa/advisory-293.html
- http://www.openwall.com/lists/oss-security/2019/10/25/8
