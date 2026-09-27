# [M] CVE-2020-12768

## Summary
Severity: Medium
Advisory: CVE-2020-12768
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-09
Source: https://osv.dev/vulnerability/CVE-2020-12768
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.6. svm_cpu_uninit in arch/x86/kvm/svm.c has a memory leak, aka CID-d80b64ff297e. NOTE: third parties dispute this issue because it's a one-time leak at the boot, the size is negligible, and it can't be triggered at will

## References
- https://usn.ubuntu.com/4411-1/
- https://usn.ubuntu.com/4412-1/
- https://usn.ubuntu.com/4413-1/
- https://www.debian.org/security/2020/dsa-4699
- https://bugzilla.suse.com/show_bug.cgi?id=1171736#c3
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=d80b64ff297e40c2b6f7d7abc1b3eba70d22a068
