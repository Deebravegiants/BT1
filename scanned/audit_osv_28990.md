# [H] rcu-tasks: Fix show_rcu_tasks_trace_gp_kthread buffer overflow

## Summary
Severity: High
Advisory: CVE-2024-38577
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38577
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

rcu-tasks: Fix show_rcu_tasks_trace_gp_kthread buffer overflow

There is a possibility of buffer overflow in
show_rcu_tasks_trace_gp_kthread() if counters, passed
to sprintf() are huge. Counter numbers, needed for this
are unrealistically high, but buffer overflow is still
possible.

Use snprintf() with buffer size instead of sprintf().

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/08186d0c5fb64a1cc4b43e009314ee6b173ed222
- https://git.kernel.org/stable/c/17c43211d45f13d1badea3942b76bf16bcc49281
- https://git.kernel.org/stable/c/1a240e138071b25944ded0f5b3e357aa99fabcb7
- https://git.kernel.org/stable/c/32d988f48ed287e676a29a15ac30701c35849aec
- https://git.kernel.org/stable/c/6593d857ce5b5b802fb73d8091ac9c84b92c1697
- https://git.kernel.org/stable/c/af7b560c88fb420099e29890aa682b8a3efc8784
- https://git.kernel.org/stable/c/cc5645fddb0ce28492b15520306d092730dffa48
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38577.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38577
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
