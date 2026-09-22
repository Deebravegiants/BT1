# [M] CVE-2019-3901

## Summary
Severity: Medium
Advisory: CVE-2019-3901
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-04-22
Source: https://osv.dev/vulnerability/CVE-2019-3901
Type: osv

## Details
A race condition in perf_event_open() allows local attackers to leak sensitive data from setuid programs. As no relevant locks (in particular the cred_guard_mutex) are held during the ptrace_may_access() call, it is possible for the specified target task to perform an execve() syscall with setuid execution before perf_event_alloc() actually attaches to it, allowing an attacker to bypass the ptrace_may_access() check and the perf_event_exit_task(current) call that is performed in install_exec_creds() during privileged execve() calls. This issue affects kernel versions before 4.8.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00041.html
- https://lists.debian.org/debian-lts-announce/2019/05/msg00042.html
- https://security.netapp.com/advisory/ntap-20190517-0005/
- http://www.securityfocus.com/bid/89937
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3901
