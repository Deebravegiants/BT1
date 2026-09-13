# [M] CVE-2020-2732

## Summary
Severity: Medium
Advisory: CVE-2020-2732
CVSS: 6.8 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2020-04-08
Source: https://osv.dev/vulnerability/CVE-2020-2732
Type: osv

## Details
A flaw was discovered in the way that the KVM hypervisor handled instruction emulation for an L2 guest when nested virtualisation is enabled. Under some circumstances, an L2 guest may trick the L0 guest into accessing sensitive L1 resources that should be inaccessible to the L2 guest.

## References
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://www.debian.org/security/2020/dsa-4698
- https://www.openwall.com/lists/oss-security/2020/02/25/3
- https://linux.oracle.com/errata/ELSA-2020-5540.html
- https://linux.oracle.com/errata/ELSA-2020-5542.html
- https://linux.oracle.com/errata/ELSA-2020-5543.html
- https://www.debian.org/security/2020/dsa-4667
- https://bugzilla.redhat.com/show_bug.cgi?id=1805135
- https://www.spinics.net/lists/kvm/msg208259.html
- https://git.kernel.org/linus/35a571346a94fb93b5b3b6a599675ef3384bc75c
- https://git.kernel.org/linus/07721feee46b4b248402133228235318199b05ec
- https://git.kernel.org/linus/e71237d3ff1abf9f3388337cfebf53b96df2020d
