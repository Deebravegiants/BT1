# [M] CVE-2019-19332

## Summary
Severity: Medium
Advisory: CVE-2019-19332
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2020-01-09
Source: https://osv.dev/vulnerability/CVE-2019-19332
Type: osv

## Details
An out-of-bounds memory write issue was found in the Linux Kernel, version 3.13 through 5.4, in the way the Linux kernel's KVM hypervisor handled the 'KVM_GET_EMULATED_CPUID' ioctl(2) request to get CPUID features emulated by the KVM hypervisor. A user or process able to access the '/dev/kvm' device could use this flaw to crash the system, resulting in a denial of service.

## References
- https://lore.kernel.org/kvm/000000000000ea5ec20598d90e50%40google.com/
- https://usn.ubuntu.com/4254-1/
- https://usn.ubuntu.com/4258-1/
- https://usn.ubuntu.com/4287-2/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://usn.ubuntu.com/4254-2/
- https://usn.ubuntu.com/4284-1/
- https://usn.ubuntu.com/4287-1/
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://security.netapp.com/advisory/ntap-20200204-0002/
- http://packetstormsecurity.com/files/155890/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-19332
- https://www.openwall.com/lists/oss-security/2019/12/16/1
