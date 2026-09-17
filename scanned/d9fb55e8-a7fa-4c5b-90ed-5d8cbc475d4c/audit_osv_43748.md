# [H] ipvs: stop estimator after disabled calc phase

## Summary
Severity: High
Advisory: CVE-2026-74670
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74670
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipvs: stop estimator after disabled calc phase

IPVS estimator kthread 0 starts with zeroed chain and tick limits until
its initial calculation phase completes. If network namespace teardown
clears ipvs->enable during that phase, ip_vs_est_calc_phase() can return
without installing positive limits.

The kthread can then continue into its main loop and drain
est_temp_list with zero chain_max, tick_max and est_max_count values.
Each enqueue consumes one available tick row, but est_count never
reaches the zero est_max_count value. After all rows are consumed, the
row lookup returns IPVS_EST_NTICKS and ip_vs_enqueue_estimator() writes
past the ticks and tick_len arrays.

Exit kthread 0 after the calculation phase if the kthread is stopping or
IPVS has been disabled. That keeps temporary estimators from being
drained after the limits failed to initialize.

Estimator kthreads can now self-exit before teardown or reload stops
kd->task. Keep an extra task reference after creation and release it
with kthread_stop_put(), so kd->task remains valid until the stop paths
consume that reference.

## References
- https://git.kernel.org/stable/c/2335dedc1922dfa889ca1f9f70370924e8e79a08
- https://git.kernel.org/stable/c/558f67f1340f803a346ecd14a69c49653111c5f4
- https://git.kernel.org/stable/c/d5122a2b2601145975d387006e517c56896e310e
- https://git.kernel.org/stable/c/de98dc5ef94b83bbb444c670c253ea02ca0f5e43
- https://git.kernel.org/stable/c/e7f34f29b330265d456943bf0b984dcecfcef9af
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74670.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74670
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
