# [H] CVE-2020-12657

## Summary
Severity: High
Advisory: CVE-2020-12657
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-05
Source: https://osv.dev/vulnerability/CVE-2020-12657
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.6.5. There is a use-after-free in block/bfq-iosched.c related to bfq_idle_slice_timer_body.

## References
- https://usn.ubuntu.com/4367-1/
- https://usn.ubuntu.com/4369-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- https://usn.ubuntu.com/4368-1/
- https://usn.ubuntu.com/4363-1/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.5
- https://security.netapp.com/advisory/ntap-20200608-0001/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=2f95fa5c955d0a9987ffdc3a095e2f4e62c5f2a9
- https://github.com/torvalds/linux/commit/2f95fa5c955d0a9987ffdc3a095e2f4e62c5f2a9
- https://patchwork.kernel.org/patch/11447049/
