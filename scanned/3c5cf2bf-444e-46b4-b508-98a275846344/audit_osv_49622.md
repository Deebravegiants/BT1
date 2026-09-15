# [H] CVE-2019-14821

## Summary
Severity: High
Advisory: CVE-2019-14821
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-09-19
Source: https://osv.dev/vulnerability/CVE-2019-14821
Type: osv

## Details
An out-of-bounds access issue was found in the Linux kernel, all versions through 5.3, in the way Linux kernel's KVM hypervisor implements the Coalesced MMIO write operation. It operates on an MMIO ring buffer 'struct kvm_coalesced_mmio' object, wherein write indices 'ring->first' and 'ring->last' value could be supplied by a host user-space process. An unprivileged host user or process with access to '/dev/kvm' device could use this flaw to crash the host kernel, resulting in a denial of service or potentially escalating privileges on the system.

## References
- http://packetstormsecurity.com/files/154951/Kernel-Live-Patch-Security-Notice-LSN-0058-1.html
- https://access.redhat.com/errata/RHSA-2019:3517
- https://lists.debian.org/debian-lts-announce/2019/09/msg00025.html
- https://security.netapp.com/advisory/ntap-20191004-0001/
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00036.html
- https://access.redhat.com/errata/RHSA-2019:3978
- https://seclists.org/bugtraq/2019/Nov/11
- https://usn.ubuntu.com/4162-1/
- https://usn.ubuntu.com/4163-1/
- http://packetstormsecurity.com/files/155212/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TRZQQQANZWQMPILZV7OTS3RGGRLLE2Q7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YW3QNMPENPFEGVTOFPSNOBL7JEIJS25P/
- https://usn.ubuntu.com/4157-2/
- https://www.debian.org/security/2019/dsa-4531
- https://access.redhat.com/errata/RHSA-2019:3309
- https://usn.ubuntu.com/4157-1/
- https://usn.ubuntu.com/4162-2/
- https://access.redhat.com/errata/RHSA-2019:3979
- https://lists.debian.org/debian-lts-announce/2019/10/msg00000.html
- https://usn.ubuntu.com/4163-2/
