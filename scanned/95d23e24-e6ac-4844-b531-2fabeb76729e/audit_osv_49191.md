# [M] CVE-2018-5244

## Summary
Severity: Medium
Advisory: CVE-2018-5244
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-01-05
Source: https://osv.dev/vulnerability/CVE-2018-5244
Type: osv

## Details
In Xen 4.10, new infrastructure was introduced as part of an overhaul to how MSR emulation happens for guests. Unfortunately, one tracking structure isn't freed when a vcpu is destroyed. This allows guest OS administrators to cause a denial of service (host OS memory consumption) by rebooting many times.

## References
- http://www.securitytracker.com/id/1040774
- http://www.securityfocus.com/bid/102433
- https://security.gentoo.org/glsa/201810-06
- https://xenbits.xen.org/xsa/advisory-253.html
