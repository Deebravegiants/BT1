# [C] CVE-2017-10920

## Summary
Severity: Critical
Advisory: CVE-2017-10920
CVSS: 10.0 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-07-05
Source: https://osv.dev/vulnerability/CVE-2017-10920
Type: osv

## Details
The grant-table feature in Xen through 4.8.x mishandles a GNTMAP_device_map and GNTMAP_host_map mapping, when followed by only a GNTMAP_host_map unmapping, which allows guest OS users to cause a denial of service (count mismanagement and memory corruption) or obtain privileged host OS access, aka XSA-224 bug 1.

## References
- http://www.securitytracker.com/id/1038734
- http://www.debian.org/security/2017/dsa-3969
- https://security.gentoo.org/glsa/201708-03
- https://security.gentoo.org/glsa/201710-17
- https://xenbits.xen.org/xsa/advisory-224.html
