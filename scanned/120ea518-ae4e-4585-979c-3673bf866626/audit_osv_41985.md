# [H] fuse-uring: Avoid queue->stopped races and set/read that value under lock

## Summary
Severity: High
Advisory: CVE-2026-64260
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64260
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

fuse-uring: Avoid queue->stopped races and set/read that value under lock

There are several readers of queue->stopped that check the value
under lock, but fuse_uring_commit_fetch() did not and actually
the value was not set under the lock in fuse_uring_abort_end_requests()
either. Especially in fuse_uring_commit_fetch it is important
to check under a lock, because due to races 'struct fuse_req'
might be freed with fuse_request_end, but another thread/cpu
might already do teardown work.

## References
- https://git.kernel.org/stable/c/39c8e925b207afceffaa5382416ed405e0223a03
- https://git.kernel.org/stable/c/4021a3a79eee551d95fe1e1e7c1b195d34ba8c08
- https://git.kernel.org/stable/c/b70a3aca16934c196f92abb17b01c1647b9bb63c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64260.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64260
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
