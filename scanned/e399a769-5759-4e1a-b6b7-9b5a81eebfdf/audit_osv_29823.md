# [H] tracing/timerlat: Only clear timer if a kthread exists

## Summary
Severity: High
Advisory: CVE-2024-46845
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46845
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing/timerlat: Only clear timer if a kthread exists

The timerlat tracer can use user space threads to check for osnoise and
timer latency. If the program using this is killed via a SIGTERM, the
threads are shutdown one at a time and another tracing instance can start
up resetting the threads before they are fully closed. That causes the
hrtimer assigned to the kthread to be shutdown and freed twice when the
dying thread finally closes the file descriptors, causing a use-after-free
bug.

Only cancel the hrtimer if the associated thread is still around. Also add
the interface_lock around the resetting of the tlat_var->kthread.

Note, this is just a quick fix that can be backported to stable. A real
fix is to have a better synchronization between the shutdown of old
threads and the starting of new ones.

## References
- https://git.kernel.org/stable/c/8a9d0d405159e9c796ddf771f7cff691c1a2bc1e
- https://git.kernel.org/stable/c/8c72f0b2c45f21cb8b00fc37f79f632d7e46c2ed
- https://git.kernel.org/stable/c/e6a53481da292d970d1edf0d8831121d1c5e2f0d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46845.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46845
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
