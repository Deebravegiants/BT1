# [H] iov_iter: fix copy_page_from_iter_atomic() if KMAP_LOCAL_FORCE_MAP

## Summary
Severity: High
Advisory: CVE-2024-50222
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50222
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

iov_iter: fix copy_page_from_iter_atomic() if KMAP_LOCAL_FORCE_MAP

generic/077 on x86_32 CONFIG_DEBUG_KMAP_LOCAL_FORCE_MAP=y with highmem,
on huge=always tmpfs, issues a warning and then hangs (interruptibly):

WARNING: CPU: 5 PID: 3517 at mm/highmem.c:622 kunmap_local_indexed+0x62/0xc9
CPU: 5 UID: 0 PID: 3517 Comm: cp Not tainted 6.12.0-rc4 #2
...
copy_page_from_iter_atomic+0xa6/0x5ec
generic_perform_write+0xf6/0x1b4
shmem_file_write_iter+0x54/0x67

Fix copy_page_from_iter_atomic() by limiting it in that case
(include/linux/skbuff.h skb_frag_must_loop() does similar).

But going forward, perhaps CONFIG_DEBUG_KMAP_LOCAL_FORCE_MAP is too
surprising, has outlived its usefulness, and should just be removed?

## References
- https://git.kernel.org/stable/c/3a303409f271dfe0987b8f79595138340497a32d
- https://git.kernel.org/stable/c/4f7ffa83fa79dd52efbaef366c850aaaae06a469
- https://git.kernel.org/stable/c/c749d9b7ebbc5716af7a95f7768634b30d9446ec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50222.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50222
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
