# [H] iavf: fix PTP use-after-free during reset

## Summary
Severity: High
Advisory: CVE-2026-43447
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43447
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

iavf: fix PTP use-after-free during reset

Commit 7c01dbfc8a1c5f ("iavf: periodically cache PHC time") introduced a
worker to cache PHC time, but failed to stop it during reset or disable.

This creates a race condition where `iavf_reset_task()` or
`iavf_disable_vf()` free adapter resources (AQ) while the worker is still
running. If the worker triggers `iavf_queue_ptp_cmd()` during teardown, it
accesses freed memory/locks, leading to a crash.

Fix this by calling `iavf_ptp_release()` before tearing down the adapter.
This ensures `ptp_clock_unregister()` synchronously cancels the worker and
cleans up the chardev before the backing resources are destroyed.

## References
- https://git.kernel.org/stable/c/1b034f2429ce6b45ce74dc266175d277acafc5c4
- https://git.kernel.org/stable/c/90cc8b2add29b57288025b51c70bc647e7cccb12
- https://git.kernel.org/stable/c/efc54fb13d79117a825fef17364315a58682c7ec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43447.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43447
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
