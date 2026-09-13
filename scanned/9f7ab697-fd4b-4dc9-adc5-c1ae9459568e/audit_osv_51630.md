# [H] CVE-2021-3653

## Summary
Severity: High
Advisory: CVE-2021-3653
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-09-29
Source: https://osv.dev/vulnerability/CVE-2021-3653
Type: osv

## Details
A flaw was found in the KVM's AMD code for supporting SVM nested virtualization. The flaw occurs when processing the VMCB (virtual machine control block) provided by the L1 guest to spawn/handle a nested guest (L2). Due to improper validation of the "int_ctl" field, this issue could allow a malicious L1 to enable AVIC support (Advanced Virtual Interrupt Controller) for the L2 guest. As a result, the L2 guest would be allowed to read/write physical pages of the host, resulting in a crash of the entire system, leak of sensitive data or potential guest-to-host escape. This flaw affects Linux kernel versions prior to 5.14-rc7.

## References
- https://lists.debian.org/debian-lts-announce/2021/10/msg00010.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00012.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1983686
- https://www.openwall.com/lists/oss-security/2021/08/16/1
- http://packetstormsecurity.com/files/165477/Kernel-Live-Patch-Security-Notice-LSN-0083-1.html
