# [H] media: tuner: xc5000: Fix use-after-free in xc5000_release

## Summary
Severity: High
Advisory: CVE-2025-39994
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39994
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.156, >=6.2.0 <6.6.111, >=6.7.0 <6.12.51, >=6.13.0 <6.16.11, >=6.17.0 <6.17.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: tuner: xc5000: Fix use-after-free in xc5000_release

The original code uses cancel_delayed_work() in xc5000_release(), which
does not guarantee that the delayed work item timer_sleep has fully
completed if it was already running. This leads to use-after-free scenarios
where xc5000_release() may free the xc5000_priv while timer_sleep is still
active and attempts to dereference the xc5000_priv.

A typical race condition is illustrated below:

CPU 0 (release thread)                 | CPU 1 (delayed work callback)
xc5000_release()                       | xc5000_do_timer_sleep()
  cancel_delayed_work()                |
  hybrid_tuner_release_state(priv)     |
    kfree(priv)                        |
                                       |   priv = container_of() // UAF

Replace cancel_delayed_work() with cancel_delayed_work_sync() to ensure
that the timer_sleep is properly canceled before the xc5000_priv memory
is deallocated.

A deadlock concern was considered: xc5000_release() is called in a process
context and is not holding any locks that the timer_sleep work item might
also need. Therefore, the use of the _sync() variant is safe here.

This bug was initially identified through static analysis.

[hverkuil: fix typo in Subject: tunner -> tuner]

## References
- https://git.kernel.org/stable/c/3f876cd47ed8bca1e28d68435845949f51f90703
- https://git.kernel.org/stable/c/40b7a19f321e65789612ebaca966472055dab48c
- https://git.kernel.org/stable/c/4266f012806fc18e46da4a04d130df59a4946f93
- https://git.kernel.org/stable/c/71ed8b81a4906cb785966910f39cf7f5ad60a69e
- https://git.kernel.org/stable/c/9a00de20ed8ba90888479749b87bc1532cded4ce
- https://git.kernel.org/stable/c/bc4ffd962ce16a154c44c68853b9d93f5b6fc4b8
- https://git.kernel.org/stable/c/df0303b4839520b84d9367c2fad65b13650a4d42
- https://git.kernel.org/stable/c/e2f5eaafc0306a76fb1cb760aae804b065b8a341
- https://git.kernel.org/stable/c/effb1c19583bca7022fa641a70766de45c6d41ac
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39994.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39994
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
