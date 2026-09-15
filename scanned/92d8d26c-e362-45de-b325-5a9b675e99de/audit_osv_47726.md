# [H] CVE-2017-10916

## Summary
Severity: High
Advisory: CVE-2017-10916
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-07-05
Source: https://osv.dev/vulnerability/CVE-2017-10916
Type: osv

## Details
The vCPU context-switch implementation in Xen through 4.8.x improperly interacts with the Memory Protection Extensions (MPX) and Protection Key (PKU) features, which makes it easier for guest OS users to defeat ASLR and other protection mechanisms, aka XSA-220.

## References
- http://www.securityfocus.com/bid/99167
- http://www.securitytracker.com/id/1038730
- http://www.debian.org/security/2017/dsa-3969
- https://security.gentoo.org/glsa/201708-03
- https://xenbits.xen.org/xsa/advisory-220.html
