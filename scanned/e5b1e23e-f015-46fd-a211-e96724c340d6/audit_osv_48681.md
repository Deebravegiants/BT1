# [H] CVE-2018-10982

## Summary
Severity: High
Advisory: CVE-2018-10982
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-05-10
Source: https://osv.dev/vulnerability/CVE-2018-10982
Type: osv

## Details
An issue was discovered in Xen through 4.10.x allowing x86 HVM guest OS users to cause a denial of service (unexpectedly high interrupt number, array overrun, and hypervisor crash) or possibly gain hypervisor privileges by setting up an HPET timer to deliver interrupts in IO-APIC mode, aka vHPET interrupt injection.

## References
- http://openwall.com/lists/oss-security/2018/05/08/2
- http://www.securityfocus.com/bid/104150
- https://security.gentoo.org/glsa/201810-06
- https://www.debian.org/security/2018/dsa-4201
- https://lists.debian.org/debian-lts-announce/2018/05/msg00015.html
- https://lists.debian.org/debian-lts-announce/2018/10/msg00009.html
- https://xenbits.xen.org/xsa/advisory-261.html
