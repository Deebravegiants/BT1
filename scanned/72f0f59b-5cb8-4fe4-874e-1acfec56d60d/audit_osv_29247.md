# [H] filelock: fix potential use-after-free in posix_lock_inode

## Summary
Severity: High
Advisory: CVE-2024-41049
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41049
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.280, >=5.5.0 <5.10.222, >=5.11.0 <5.15.163, >=5.16.0 <6.1.100, >=6.2.0 <6.6.41, >=6.6.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

filelock: fix potential use-after-free in posix_lock_inode

Light Hsieh reported a KASAN UAF warning in trace_posix_lock_inode().
The request pointer had been changed earlier to point to a lock entry
that was added to the inode's list. However, before the tracepoint could
fire, another task raced in and freed that lock.

Fix this by moving the tracepoint inside the spinlock, which should
ensure that this doesn't happen.

## References
- https://git.kernel.org/stable/c/02a8964260756c70b20393ad4006948510ac9967
- https://git.kernel.org/stable/c/116599f6a26906cf33f67975c59f0692ecf7e9b2
- https://git.kernel.org/stable/c/1b3ec4f7c03d4b07bad70697d7e2f4088d2cfe92
- https://git.kernel.org/stable/c/1cbbb3d9475c403ebedc327490c7c2b991398197
- https://git.kernel.org/stable/c/432b06b69d1d354a171f7499141116536579eb6a
- https://git.kernel.org/stable/c/5cb36e35bc10ea334810937990c2b9023dacb1b0
- https://git.kernel.org/stable/c/7d4c14f4b511fd4c0dc788084ae59b4656ace58b
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41049.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41049
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
