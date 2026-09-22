# [M] CVE-2018-7542

## Summary
Severity: Medium
Advisory: CVE-2018-7542
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-02-27
Source: https://osv.dev/vulnerability/CVE-2018-7542
Type: osv

## Details
An issue was discovered in Xen 4.8.x through 4.10.x allowing x86 PVH guest OS users to cause a denial of service (NULL pointer dereference and hypervisor crash) by leveraging the mishandling of configurations that lack a Local APIC.

## References
- http://www.securitytracker.com/id/1040776
- https://www.debian.org/security/2018/dsa-4131
- https://xenbits.xen.org/xsa/advisory-256.html
- https://security.gentoo.org/glsa/201810-06
