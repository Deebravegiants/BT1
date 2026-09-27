# [M] CVE-2015-8553

## Summary
Severity: Medium
Advisory: CVE-2015-8553
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2016-04-13
Source: https://osv.dev/vulnerability/CVE-2015-8553
Type: osv

## Details
Xen allows guest OS users to obtain sensitive information from uninitialized locations in host OS kernel memory by not enabling memory and I/O decoding control bits.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2015-0777.

## References
- http://xenbits.xen.org/xsa/advisory-120.html
- https://www.debian.org/security/2019/dsa-4497
- http://xenbits.xen.org/xsa/advisory-120.html
- https://seclists.org/bugtraq/2019/Aug/18
