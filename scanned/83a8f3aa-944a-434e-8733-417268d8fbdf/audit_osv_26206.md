# [H] tee: amdtee: fix use-after-free vulnerability in amdtee_close_session

## Summary
Severity: High
Advisory: CVE-2023-52503
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52503
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.199, >=5.11.0 <5.15.136, >=5.16.0 <6.1.59, >=6.2.0 <6.5.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

tee: amdtee: fix use-after-free vulnerability in amdtee_close_session

There is a potential race condition in amdtee_close_session that may
cause use-after-free in amdtee_open_session. For instance, if a session
has refcount == 1, and one thread tries to free this session via:

    kref_put(&sess->refcount, destroy_session);

the reference count will get decremented, and the next step would be to
call destroy_session(). However, if in another thread,
amdtee_open_session() is called before destroy_session() has completed
execution, alloc_session() may return 'sess' that will be freed up
later in destroy_session() leading to use-after-free in
amdtee_open_session.

To fix this issue, treat decrement of sess->refcount and removal of
'sess' from session list in destroy_session() as a critical section, so
that it is executed atomically.

## References
- https://git.kernel.org/stable/c/1680c82929bc14d706065f123dab77f2f1293116
- https://git.kernel.org/stable/c/1c95574350cd63bc3c5c2fa06658010768f2a0ce
- https://git.kernel.org/stable/c/60c3e7a00db954947c265b55099c21b216f2a05c
- https://git.kernel.org/stable/c/da7ce52a2f6c468946195b116615297d3d113a27
- https://git.kernel.org/stable/c/f4384b3e54ea813868bb81a861bf5b2406e15d8f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52503.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52503
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
