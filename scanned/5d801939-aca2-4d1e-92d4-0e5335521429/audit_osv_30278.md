# [M] signal: restore the override_rlimit logic

## Summary
Severity: Medium
Advisory: CVE-2024-50271
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50271
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

signal: restore the override_rlimit logic

Prior to commit d64696905554 ("Reimplement RLIMIT_SIGPENDING on top of
ucounts") UCOUNT_RLIMIT_SIGPENDING rlimit was not enforced for a class of
signals.  However now it's enforced unconditionally, even if
override_rlimit is set.  This behavior change caused production issues.  

For example, if the limit is reached and a process receives a SIGSEGV
signal, sigqueue_alloc fails to allocate the necessary resources for the
signal delivery, preventing the signal from being delivered with siginfo. 
This prevents the process from correctly identifying the fault address and
handling the error.  From the user-space perspective, applications are
unaware that the limit has been reached and that the siginfo is
effectively 'corrupted'.  This can lead to unpredictable behavior and
crashes, as we observed with java applications.

Fix this by passing override_rlimit into inc_rlimit_get_ucounts() and skip
the comparison to max there if override_rlimit is set.  This effectively
restores the old behavior.

## References
- https://git.kernel.org/stable/c/012f4d5d25e9ef92ee129bd5aa7aa60f692681e1
- https://git.kernel.org/stable/c/0208ea17a1e4456fbfe555f13ae5c28f3d671e40
- https://git.kernel.org/stable/c/4877d9b2a2ebad3ae240127aaa4cb8258b145cf7
- https://git.kernel.org/stable/c/9e05e5c7ee8758141d2db7e8fea2cab34500c6ed
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50271.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50271
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
