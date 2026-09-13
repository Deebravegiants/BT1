# [H] wifi: ath6kl: fix use-after-free in aggr_reset_state()

## Summary
Severity: High
Advisory: CVE-2026-68198
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68198
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath6kl: fix use-after-free in aggr_reset_state()

The aggr_reset_state() function uses timer_delete() (non-synchronous)
for the aggregation timer before proceeding to delete TID state and
before the structure is freed by callers like aggr_module_destroy().

If the timer callback (aggr_timeout) is executing when aggr_reset_state()
is called, the callback will continue to access aggr_conn fields like
rx_tid[] and stat[] which may be freed immediately after by
kfree(aggr_info->aggr_conn) in aggr_module_destroy().

Additionally, the timer callback can re-arm itself via mod_timer() while
aggr_reset_state() is running, creating a more complex race condition.

Use timer_delete_sync() instead to ensure any running timer callback
has completed before returning.

## References
- https://git.kernel.org/stable/c/17ff29cd8dbc977c97788a5f7c011ec807b58242
- https://git.kernel.org/stable/c/18965470d41e69d3fc10eb62afae29d10f4cdfd1
- https://git.kernel.org/stable/c/2132a6db05846dd2318857d00e0c1291f9e41b29
- https://git.kernel.org/stable/c/64af6534a085f49d6ed33338a19ab9cf0d0523c9
- https://git.kernel.org/stable/c/a1bac650b2d6b1baab1f3e78e2e007a6e2948dde
- https://git.kernel.org/stable/c/a3313111b5d9046af60b370c93eec105b27380c1
- https://git.kernel.org/stable/c/b5d618fd61b9069b4c0a6b487022dd3117ad5acc
- https://git.kernel.org/stable/c/ba7debb4dd6427386862220e8335a53a4bfc235d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68198.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68198
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
