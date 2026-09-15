# [H] CVE-2019-13233

## Summary
Severity: High
Advisory: CVE-2019-13233
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-04
Source: https://osv.dev/vulnerability/CVE-2019-13233
Type: osv

## Details
In arch/x86/lib/insn-eval.c in the Linux kernel before 5.1.9, there is a use-after-free for access to an LDT entry because of a race condition between modify_ldt() and a #BR exception for an MPX bounds violation.

## References
- http://packetstormsecurity.com/files/154408/Kernel-Live-Patch-Security-Notice-LSN-0055-1.html
- https://usn.ubuntu.com/4118-1/
- https://support.f5.com/csp/article/K13331647?utm_source=f5support&amp%3Butm_medium=RSS
- https://usn.ubuntu.com/4093-1/
- https://usn.ubuntu.com/4094-1/
- https://usn.ubuntu.com/4117-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00025.html
- https://seclists.org/bugtraq/2019/Aug/13
- https://access.redhat.com/errata/RHSA-2019:3517
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.9
- https://security.netapp.com/advisory/ntap-20190806-0001/
- https://access.redhat.com/errata/RHSA-2019:3309
- https://www.debian.org/security/2019/dsa-4495
- https://github.com/torvalds/linux/commit/de9f869616dd95e95c00bdd6b0fcd3421e8a4323
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1879
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=de9f869616dd95e95c00bdd6b0fcd3421e8a4323
