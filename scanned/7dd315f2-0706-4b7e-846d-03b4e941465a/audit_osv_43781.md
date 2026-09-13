# [H] enic: fix tx_hang_reset use-after-free on device removal

## Summary
Severity: High
Advisory: CVE-2026-74725
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74725
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

enic: fix tx_hang_reset use-after-free on device removal

enic_remove() cancels the reset and change_mtu_work items but does not
cancel tx_hang_reset. A TX timeout that fires while the device is being
removed can schedule enic_tx_hang_reset() so that it runs after
free_netdev(), resulting in a use-after-free.

cancel_work_sync() alone is not sufficient here: the still-live watchdog
and notify paths can re-schedule these work items in the window between
the cancel and unregister_netdev(). Use disable_work_sync(), which
cancels the work and blocks any subsequent schedule_work() from
requeuing it, and apply it to the reset and change_mtu_work items as
well so the same requeue race is closed for all teardown work.

## References
- https://git.kernel.org/stable/c/4f3464fc6c1f26afc504fd525c574f2bc14c9d42
- https://git.kernel.org/stable/c/8619865f34fb3b130b567855382a5c4aadd522b9
- https://git.kernel.org/stable/c/e506e704b74748ffd0e1c92a7453ca2a959f832b
- https://git.kernel.org/stable/c/ec680ea4ba1bca92a767fb7e7869758bfdd886e3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74725.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74725
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
