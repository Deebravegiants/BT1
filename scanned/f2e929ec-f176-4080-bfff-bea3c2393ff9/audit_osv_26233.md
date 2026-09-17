# [M] KVM: s390: fix setting of fpc register

## Summary
Severity: Medium
Advisory: CVE-2023-52597
Ecosystem: Linux
CVSS: 4.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2024-03-06
Source: https://osv.dev/vulnerability/CVE-2023-52597
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <4.19.307, >=4.20.0 <5.4.269, >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.77, >=6.2.0 <6.6.16, >=6.7.0 <6.7.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: s390: fix setting of fpc register

kvm_arch_vcpu_ioctl_set_fpu() allows to set the floating point control
(fpc) register of a guest cpu. The new value is tested for validity by
temporarily loading it into the fpc register.

This may lead to corruption of the fpc register of the host process:
if an interrupt happens while the value is temporarily loaded into the fpc
register, and within interrupt context floating point or vector registers
are used, the current fp/vx registers are saved with save_fpu_regs()
assuming they belong to user space and will be loaded into fp/vx registers
when returning to user space.

test_fp_ctl() restores the original user space / host process fpc register
value, however it will be discarded, when returning to user space.

In result the host process will incorrectly continue to run with the value
that was supposed to be used for a guest cpu.

Fix this by simply removing the test. There is another test right before
the SIE context is entered which will handles invalid values.

This results in a change of behaviour: invalid values will now be accepted
instead of that the ioctl fails with -EINVAL. This seems to be acceptable,
given that this interface is most likely not used anymore, and this is in
addition the same behaviour implemented with the memory mapped interface
(replace invalid values with zero) - see sync_regs() in kvm-s390.c.

## References
- https://git.kernel.org/stable/c/0671f42a9c1084db10d68ac347d08dbf6689ecb3
- https://git.kernel.org/stable/c/150a3a3871490e8c454ffbac2e60abeafcecff99
- https://git.kernel.org/stable/c/2823db0010c400e4b2b12d02aa5d0d3ecb15d7c7
- https://git.kernel.org/stable/c/3a04410b0bc7e056e0843ac598825dd359246d18
- https://git.kernel.org/stable/c/5e63c9ae8055109d805aacdaf2a4fe2c3b371ba1
- https://git.kernel.org/stable/c/732a3bea7aba5b15026ea42d14953c3425cc7dc2
- https://git.kernel.org/stable/c/b988b1bb0053c0dcd26187d29ef07566a565cf55
- https://git.kernel.org/stable/c/c87d7d910775a025e230fd6359b60627e392460f
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52597.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52597
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
