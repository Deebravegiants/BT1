# [H] wifi: cfg80211: cancel sched scan results work on unregister

## Summary
Severity: High
Advisory: CVE-2026-68414
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68414
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.0.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: cfg80211: cancel sched scan results work on unregister

cfg80211_sched_scan_results() can queue rdev->sched_scan_res_wk from a
driver result notification while a scheduled scan request is present. The
work callback recovers the containing cfg80211_registered_device and then
locks the wiphy and walks the scheduled-scan request list.

wiphy_unregister() already makes the wiphy unreachable and drains rdev work
items before cfg80211_dev_free() can release the object, but it does not
drain sched_scan_res_wk. A queued or running result work item can therefore
cross the unregister/free boundary and access freed rdev state.

The buggy scenario involves two paths, with each column showing the order
within that path:

scheduled-scan result path:        unregister/free path:
1. cfg80211_sched_scan_results()   1. interface teardown stops and
   queues rdev->sched_scan_res_wk.    removes the scheduled scan request.
2. cfg80211_wq starts the work     2. wiphy_unregister() drains other
   item and recovers rdev.            rdev work items.
3. The worker locks rdev->wiphy    3. cfg80211_dev_free() destroys and
   and walks rdev state.              frees rdev.

Cancel sched_scan_res_wk in wiphy_unregister() alongside the other rdev
work items. cancel_work_sync() removes a pending result notification and
waits for an already running callback, so cfg80211_dev_free() cannot free
rdev while this work item is still active.

Validation reproduced this kernel report:
BUG: KASAN: use-after-free in cfg80211_sched_scan_results_wk+0x4a6/0x530
Workqueue: cfg80211 cfg80211_sched_scan_results_wk [cfg80211]
Read of size 8
Call trace:
  dump_stack_lvl+0x66/0xa0
  print_report+0xce/0x630
  cfg80211_sched_scan_results_wk+0x4a6/0x530
  srso_alias_return_thunk+0x5/0xfbef5
  __virt_addr_valid+0x224/0x430
  kasan_report+0xac/0xe0
  lockdep_hardirqs_on_prepare+0xea/0x1a0
  process_one_work+0x8d0/0x18f0 (kernel/workqueue.c:3212)
  lock_is_held_type+0x8f/0x100
  worker_thread+0x5ad/0xfd0
  __kthread_parkme+0xc6/0x200
  kthread+0x31e/0x410
  trace_hardirqs_on+0x1a/0x170
  ret_from_fork+0x576/0x810
  __switch_to+0x57e/0xe20
  __switch_to_asm+0x33/0x70
  ret_from_fork_asm+0x1a/0x30

## References
- https://git.kernel.org/stable/c/308ffdf575560d7e7b8b21f1e3ca6276630f73bf
- https://git.kernel.org/stable/c/3368457b4871ae8f0f88d19c9a3e6270e850ede6
- https://git.kernel.org/stable/c/9293574ac208d18c11073538851fb69355beb3b5
- https://git.kernel.org/stable/c/b119c70b24776c8ab2a2c0515397b3b0ad4e66cd
- https://git.kernel.org/stable/c/b51b42b974461fd0f688baad85f10e2b8ab215c5
- https://git.kernel.org/stable/c/c0fa1f3a4b021a5c6373169fd6c9bb4261d676a0
- https://git.kernel.org/stable/c/edf0730be33696a1bd142792830d392129e495cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68414.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68414
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
