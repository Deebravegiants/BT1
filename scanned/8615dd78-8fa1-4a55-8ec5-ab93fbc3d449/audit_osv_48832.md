# [M] CVE-2018-15468

## Summary
Severity: Medium
Advisory: CVE-2018-15468
CVSS: 6.0 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-08-17
Source: https://osv.dev/vulnerability/CVE-2018-15468
Type: osv

## Details
An issue was discovered in Xen through 4.11.x. The DEBUGCTL MSR contains several debugging features, some of which virtualise cleanly, but some do not. In particular, Branch Trace Store is not virtualised by the processor, and software has to be careful to configure it suitably not to lock up the core. As a result, it must only be available to fully trusted guests. Unfortunately, in the case that vPMU is disabled, all value checking was skipped, allowing the guest to choose any MSR_DEBUGCTL setting it likes. A malicious or buggy guest administrator (on Intel x86 HVM or PVH) can lock up the entire host, causing a Denial of Service.

## References
- http://xenbits.xen.org/xsa/advisory-269.html
- https://security.gentoo.org/glsa/201810-06
