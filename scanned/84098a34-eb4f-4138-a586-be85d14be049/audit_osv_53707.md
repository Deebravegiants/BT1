# [H] CVE-2023-1872

## Summary
Severity: High
Advisory: CVE-2023-1872
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-12
Source: https://osv.dev/vulnerability/CVE-2023-1872
Type: osv

## Details
A use-after-free vulnerability in the Linux Kernel io_uring system can be exploited to achieve local privilege escalation.

The io_file_get_fixed function lacks the presence of ctx->uring_lock which can lead to a Use-After-Free vulnerability due a race condition with fixed files getting unregistered.

We recommend upgrading past commit da24142b1ef9fd5d36b76e36bab328a5b27523e8.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://security.netapp.com/advisory/ntap-20230601-0002/
- http://packetstormsecurity.com/files/173087/Kernel-Live-Patch-Security-Notice-LSN-0095-1.html
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?h=linux-5.10.y&id=da24142b1ef9fd5d36b76e36bab328a5b27523e8
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?h=linux-5.10.y&id=08681391b84da27133deefaaddefd0acfa90c2be
