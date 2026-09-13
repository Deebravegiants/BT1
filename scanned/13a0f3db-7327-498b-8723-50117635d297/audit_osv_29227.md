# [H] filelock: Remove locks reliably when fcntl/close race is detected

## Summary
Severity: High
Advisory: CVE-2024-41012
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-23
Source: https://osv.dev/vulnerability/CVE-2024-41012
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.13 <4.19.319, >=4.20.0 <5.4.281, >=5.5.0 <5.10.223, >=5.11.0 <5.15.164, >=5.16.0 <6.1.101, >=6.2.0 <6.6.42, >=6.7.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

filelock: Remove locks reliably when fcntl/close race is detected

When fcntl_setlk() races with close(), it removes the created lock with
do_lock_file_wait().
However, LSMs can allow the first do_lock_file_wait() that created the lock
while denying the second do_lock_file_wait() that tries to remove the lock.
Separately, posix_lock_file() could also fail to
remove a lock due to GFP_KERNEL allocation failure (when splitting a range
in the middle).

After the bug has been triggered, use-after-free reads will occur in
lock_get_status() when userspace reads /proc/locks. This can likely be used
to read arbitrary kernel memory, but can't corrupt kernel memory.

Fix it by calling locks_remove_posix() instead, which is designed to
reliably get rid of POSIX locks associated with the given file and
files_struct and is also used by filp_flush().

## References
- https://git.kernel.org/stable/c/3cad1bc010416c6dd780643476bc59ed742436b9
- https://git.kernel.org/stable/c/52c87ab18c76c14d7209646ccb3283b3f5d87b22
- https://git.kernel.org/stable/c/5661b9c7ec189406c2dde00837aaa4672efb6240
- https://git.kernel.org/stable/c/5f5d0799eb0a01d550c21b7894e26b2d9db55763
- https://git.kernel.org/stable/c/b6d223942c34057fdfd8f149e763fa823731b224
- https://git.kernel.org/stable/c/d30ff33040834c3b9eee29740acd92f9c7ba2250
- https://git.kernel.org/stable/c/dc2ce1dfceaa0767211a9d963ddb029ab21c4235
- https://git.kernel.org/stable/c/ef8fc41cd6f95f9a4a3470f085aecf350569a0b3
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41012.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41012
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
