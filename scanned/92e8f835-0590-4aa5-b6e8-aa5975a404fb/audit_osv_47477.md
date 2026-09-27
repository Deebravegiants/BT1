# [M] CVE-2016-6259

## Summary
Severity: Medium
Advisory: CVE-2016-6259
CVSS: 6.2 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-02
Source: https://osv.dev/vulnerability/CVE-2016-6259
Type: osv

## Details
Xen 4.5.x through 4.7.x do not implement Supervisor Mode Access Prevention (SMAP) whitelisting in 32-bit exception and event delivery, which allows local 32-bit PV guest OS kernels to cause a denial of service (hypervisor and VM crash) by triggering a safety check.

## References
- http://www.securityfocus.com/bid/92130
- http://www.securitytracker.com/id/1036447
- http://support.citrix.com/article/CTX214954
- http://xenbits.xen.org/xsa/advisory-183.html
- http://xenbits.xen.org/xsa/xsa183-4.6.patch
- http://xenbits.xen.org/xsa/xsa183-unstable.patch
