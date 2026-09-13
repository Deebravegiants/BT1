# [H] CVE-2017-17053

## Summary
Severity: High
Advisory: CVE-2017-17053
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-29
Source: https://osv.dev/vulnerability/CVE-2017-17053
Type: osv

## Details
The init_new_context function in arch/x86/include/asm/mmu_context.h in the Linux kernel before 4.12.10 does not correctly handle errors from LDT table allocation when forking a new process, allowing a local attacker to achieve a use-after-free or possibly have unspecified other impact by running a specially crafted program. This vulnerability only affected kernels built with CONFIG_MODIFY_LDT_SYSCALL=y.

## References
- http://www.securityfocus.com/bid/102010
- https://access.redhat.com/errata/RHSA-2018:0676
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.12.10
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ccd5b3235180eef3cfec337df1c8554ab151b5cc
- https://github.com/torvalds/linux/commit/ccd5b3235180eef3cfec337df1c8554ab151b5cc
