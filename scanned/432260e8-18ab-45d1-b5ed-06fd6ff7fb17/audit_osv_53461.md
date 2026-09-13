# [H] CVE-2022-4378

## Summary
Severity: High
Advisory: CVE-2022-4378
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-05
Source: https://osv.dev/vulnerability/CVE-2022-4378
Type: osv

## Details
A stack overflow flaw was found in the Linux kernel's SYSCTL subsystem in how a user changes certain kernel parameters and variables. This flaw allows a local user to crash or potentially escalate their privileges on the system.

## References
- http://packetstormsecurity.com/files/171289/Kernel-Live-Patch-Security-Notice-LNS-0092-1.html
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/stable-queue.git/tree/queue-6.0/proc-avoid-integer-type-confusion-in-get_proc_long.patch
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/stable-queue.git/tree/queue-6.0/proc-proc_skip_spaces-shouldn-t-think-it-is-working-on-c-strings.patch
- https://seclists.org/oss-sec/2022/q4/178
- https://bugzilla.redhat.com/show_bug.cgi?id=2152548
