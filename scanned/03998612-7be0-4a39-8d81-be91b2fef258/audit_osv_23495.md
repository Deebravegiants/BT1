# [C] net: mana: Fix race on per-CQ variable napi work_done

## Summary
Severity: Critical
Advisory: CVE-2022-48985
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-48985
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.83, >=5.16.0 <6.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mana: Fix race on per-CQ variable napi work_done

After calling napi_complete_done(), the NAPIF_STATE_SCHED bit may be
cleared, and another CPU can start napi thread and access per-CQ variable,
cq->work_done. If the other thread (for example, from busy_poll) sets
it to a value >= budget, this thread will continue to run when it should
stop, and cause memory corruption and panic.

To fix this issue, save the per-CQ work_done variable in a local variable
before napi_complete_done(), so it won't be corrupted by a possible
concurrent thread after napi_complete_done().

Also, add a flag bit to advertise to the NIC firmware: the NAPI work_done
variable race is fixed, so the driver is able to reliably support features
like busy_poll.

## References
- https://git.kernel.org/stable/c/18010ff776fa42340efc428b3ea6d19b3e7c7b21
- https://git.kernel.org/stable/c/6740d8572ccd1bca50d8a1ca2bedc333f50ed5f3
- https://git.kernel.org/stable/c/fe50a9bbeb1f042e756c5cfa7708112c944368de
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48985.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48985
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
