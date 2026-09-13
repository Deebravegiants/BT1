# [M] CVE-2016-10025

## Summary
Severity: Medium
Advisory: CVE-2016-10025
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-26
Source: https://osv.dev/vulnerability/CVE-2016-10025
Type: osv

## Details
VMFUNC emulation in Xen 4.6.x through 4.8.x on x86 systems using AMD virtualization extensions (aka SVM) allows local HVM guest OS users to cause a denial of service (hypervisor crash) by leveraging a missing NULL pointer check.

## References
- http://www.securityfocus.com/bid/95026
- http://www.securitytracker.com/id/1037518
- http://xenbits.xen.org/xsa/advisory-203.html
- https://support.citrix.com/article/CTX219378
