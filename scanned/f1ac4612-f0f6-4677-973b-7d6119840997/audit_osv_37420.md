# [H] wifi: cfg80211: cancel pmsr_free_wk in cfg80211_pmsr_wdev_down

## Summary
Severity: High
Advisory: CVE-2026-31548
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31548
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: cfg80211: cancel pmsr_free_wk in cfg80211_pmsr_wdev_down

When the nl80211 socket that originated a PMSR request is
closed, cfg80211_release_pmsr() sets the request's nl_portid
to zero and schedules pmsr_free_wk to process the abort
asynchronously. If the interface is concurrently torn down
before that work runs, cfg80211_pmsr_wdev_down() calls
cfg80211_pmsr_process_abort() directly. However, the already-
scheduled pmsr_free_wk work item remains pending and may run
after the interface has been removed from the driver. This
could cause the driver's abort_pmsr callback to operate on a
torn-down interface, leading to undefined behavior and
potential crashes.

Cancel pmsr_free_wk synchronously in cfg80211_pmsr_wdev_down()
before calling cfg80211_pmsr_process_abort(). This ensures any
pending or in-progress work is drained before interface teardown
proceeds, preventing the work from invoking the driver abort
callback after the interface is gone.

## References
- https://git.kernel.org/stable/c/28d3551f8d8cb3aec7497894d94150fe84d20e5e
- https://git.kernel.org/stable/c/37e776e2e0a523731e2470dce6d563f0e8632a40
- https://git.kernel.org/stable/c/6dccbc9f3e1d38565dff7730d2b7d1e8b16c9b09
- https://git.kernel.org/stable/c/72b7ea786b8e570ae11149e9089859a4a8634a13
- https://git.kernel.org/stable/c/a1b7a843f12a0c3e9d3a2ca607ce451916ef42cf
- https://git.kernel.org/stable/c/d32c07ef1880fe20cf4ab223dbfedc9c0b2816aa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31548.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31548
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
