# [H] bpf: Defer work in bpf_timer_cancel_and_free

## Summary
Severity: High
Advisory: CVE-2024-41045
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41045
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Defer work in bpf_timer_cancel_and_free

Currently, the same case as previous patch (two timer callbacks trying
to cancel each other) can be invoked through bpf_map_update_elem as
well, or more precisely, freeing map elements containing timers. Since
this relies on hrtimer_cancel as well, it is prone to the same deadlock
situation as the previous patch.

It would be sufficient to use hrtimer_try_to_cancel to fix this problem,
as the timer cannot be enqueued after async_cancel_and_free. Once
async_cancel_and_free has been done, the timer must be reinitialized
before it can be armed again. The callback running in parallel trying to
arm the timer will fail, and freeing bpf_hrtimer without waiting is
sufficient (given kfree_rcu), and bpf_timer_cb will return
HRTIMER_NORESTART, preventing the timer from being rearmed again.

However, there exists a UAF scenario where the callback arms the timer
before entering this function, such that if cancellation fails (due to
timer callback invoking this routine, or the target timer callback
running concurrently). In such a case, if the timer expiration is
significantly far in the future, the RCU grace period expiration
happening before it will free the bpf_hrtimer state and along with it
the struct hrtimer, that is enqueued.

Hence, it is clear cancellation needs to occur after
async_cancel_and_free, and yet it cannot be done inline due to deadlock
issues. We thus modify bpf_timer_cancel_and_free to defer work to the
global workqueue, adding a work_struct alongside rcu_head (both used at
_different_ points of time, so can share space).

Update existing code comments to reflect the new state of affairs.

## References
- https://git.kernel.org/stable/c/7aa5a19279c3639ae8b758b63f05d0c616a39fa1
- https://git.kernel.org/stable/c/a6fcd19d7eac1335eb76bc16b6a66b7f574d1d69
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41045.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41045
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
