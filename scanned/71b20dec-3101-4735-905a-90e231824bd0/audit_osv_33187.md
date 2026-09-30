# [H] wifi: brcmfmac: fix use-after-free when rescheduling brcmf_btcoex_info work

## Summary
Severity: High
Advisory: CVE-2025-39863
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-39863
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.15.210, >=5.16.0 <6.1.167, >=6.2.0 <6.6.105, >=6.7.0 <6.12.46, >=6.13.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: brcmfmac: fix use-after-free when rescheduling brcmf_btcoex_info work

The brcmf_btcoex_detach() only shuts down the btcoex timer, if the
flag timer_on is false. However, the brcmf_btcoex_timerfunc(), which
runs as timer handler, sets timer_on to false. This creates critical
race conditions:

1.If brcmf_btcoex_detach() is called while brcmf_btcoex_timerfunc()
is executing, it may observe timer_on as false and skip the call to
timer_shutdown_sync().

2.The brcmf_btcoex_timerfunc() may then reschedule the brcmf_btcoex_info
worker after the cancel_work_sync() has been executed, resulting in
use-after-free bugs.

The use-after-free bugs occur in two distinct scenarios, depending on
the timing of when the brcmf_btcoex_info struct is freed relative to
the execution of its worker thread.

Scenario 1: Freed before the worker is scheduled

The brcmf_btcoex_info is deallocated before the worker is scheduled.
A race condition can occur when schedule_work(&bt_local->work) is
called after the target memory has been freed. The sequence of events
is detailed below:

CPU0                           | CPU1
brcmf_btcoex_detach            | brcmf_btcoex_timerfunc
                               |   bt_local->timer_on = false;
  if (cfg->btcoex->timer_on)   |
    ...                        |
  cancel_work_sync();          |
  ...                          |
  kfree(cfg->btcoex); // FREE  |
                               |   schedule_work(&bt_local->work); // USE

Scenario 2: Freed after the worker is scheduled

The brcmf_btcoex_info is freed after the worker has been scheduled
but before or during its execution. In this case, statements within
the brcmf_btcoex_handler() — such as the container_of macro and
subsequent dereferences of the brcmf_btcoex_info object will cause
a use-after-free access. The following timeline illustrates this
scenario:

CPU0                            | CPU1
brcmf_btcoex_detach             | brcmf_btcoex_timerfunc
                                |   bt_local->timer_on = false;
  if (cfg->btcoex->timer_on)    |
    ...                         |
  cancel_work_sync();           |
  ...                           |   schedule_work(); // Reschedule
                                |
  kfree(cfg->btcoex); // FREE   |   brcmf_btcoex_handler() // Worker
  /*                            |     btci = container_of(....); // USE
   The kfree() above could      |     ...
   also occur at any point      |     btci-> // USE
   during the worker's execution|
   */                           |

To resolve the race conditions, drop the conditional check and call
timer_shutdown_sync() directly. It can deactivate the timer reliably,
regardless of its current state. Once stopped, the timer_on state is
then set to false.

## References
- https://git.kernel.org/stable/c/2f6fbc8e04ca1d1d5c560be694199f847229c625
- https://git.kernel.org/stable/c/3e789f8475f6c857c88de5c5bf4b24b11a477dd7
- https://git.kernel.org/stable/c/9cb83d4be0b9b697eae93d321e0da999f9cdfcfc
- https://git.kernel.org/stable/c/ae58f70bde0433f27ef4b388ab50634736607bf6
- https://git.kernel.org/stable/c/c75600e69e66a751cc046cd9c407b942f298d852
- https://git.kernel.org/stable/c/f1150153c4e5940fe49ab51136343c5b4fe49d63
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39863.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39863
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
