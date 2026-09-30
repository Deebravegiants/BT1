# [M] NFSv4.2: fix reference count leaks in _nfs42_proc_copy_notify()

## Summary
Severity: Medium
Advisory: CVE-2022-49103
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49103
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.111, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSv4.2: fix reference count leaks in _nfs42_proc_copy_notify()

[You don't often get email from xiongx18@fudan.edu.cn. Learn why this is important at http://aka.ms/LearnAboutSenderIdentification.]

The reference counting issue happens in two error paths in the
function _nfs42_proc_copy_notify(). In both error paths, the function
simply returns the error code and forgets to balance the refcount of
object `ctx`, bumped by get_nfs_open_context() earlier, which may
cause refcount leaks.

Fix it by balancing refcount of the `ctx` object before the function
returns in both error paths.

## References
- https://git.kernel.org/stable/c/9b9feec97c1fc7dd9bb69f62c4905cddf1801599
- https://git.kernel.org/stable/c/b37f482ba9f0e6382c188e3fccf6c4b2fdc938eb
- https://git.kernel.org/stable/c/b7f114edd54326f730a754547e7cfb197b5bc132
- https://git.kernel.org/stable/c/f46f632f9cfae4b2e3635fa58840a8ec584c42e3
- https://git.kernel.org/stable/c/fb73bf6305f4eb8f0cf9a61ee874d55f019d6dc4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49103.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49103
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
