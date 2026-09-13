# [H] drm/i915/gt: fix refcount underflow in intel_engine_park_heartbeat

## Summary
Severity: High
Advisory: CVE-2026-31656
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31656
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.258, >=5.11.0 <5.15.203, >=5.16.0 <6.1.169, >=6.2.0 <6.6.135, >=6.7.0 <6.12.82, >=6.13.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915/gt: fix refcount underflow in intel_engine_park_heartbeat

A use-after-free / refcount underflow is possible when the heartbeat
worker and intel_engine_park_heartbeat() race to release the same
engine->heartbeat.systole request.

The heartbeat worker reads engine->heartbeat.systole and calls
i915_request_put() on it when the request is complete, but clears
the pointer in a separate, non-atomic step. Concurrently, a request
retirement on another CPU can drop the engine wakeref to zero, triggering
__engine_park() -> intel_engine_park_heartbeat(). If the heartbeat
timer is pending at that point, cancel_delayed_work() returns true and
intel_engine_park_heartbeat() reads the stale non-NULL systole pointer
and calls i915_request_put() on it again, causing a refcount underflow:

```
<4> [487.221889] Workqueue: i915-unordered engine_retire [i915]
<4> [487.222640] RIP: 0010:refcount_warn_saturate+0x68/0xb0
...
<4> [487.222707] Call Trace:
<4> [487.222711]  <TASK>
<4> [487.222716]  intel_engine_park_heartbeat.part.0+0x6f/0x80 [i915]
<4> [487.223115]  intel_engine_park_heartbeat+0x25/0x40 [i915]
<4> [487.223566]  __engine_park+0xb9/0x650 [i915]
<4> [487.223973]  ____intel_wakeref_put_last+0x2e/0xb0 [i915]
<4> [487.224408]  __intel_wakeref_put_last+0x72/0x90 [i915]
<4> [487.224797]  intel_context_exit_engine+0x7c/0x80 [i915]
<4> [487.225238]  intel_context_exit+0xf1/0x1b0 [i915]
<4> [487.225695]  i915_request_retire.part.0+0x1b9/0x530 [i915]
<4> [487.226178]  i915_request_retire+0x1c/0x40 [i915]
<4> [487.226625]  engine_retire+0x122/0x180 [i915]
<4> [487.227037]  process_one_work+0x239/0x760
<4> [487.227060]  worker_thread+0x200/0x3f0
<4> [487.227068]  ? __pfx_worker_thread+0x10/0x10
<4> [487.227075]  kthread+0x10d/0x150
<4> [487.227083]  ? __pfx_kthread+0x10/0x10
<4> [487.227092]  ret_from_fork+0x3d4/0x480
<4> [487.227099]  ? __pfx_kthread+0x10/0x10
<4> [487.227107]  ret_from_fork_asm+0x1a/0x30
<4> [487.227141]  </TASK>
```

Fix this by replacing the non-atomic pointer read + separate clear with
xchg() in both racing paths. xchg() is a single indivisible hardware
instruction that atomically reads the old pointer and writes NULL. This
guarantees only one of the two concurrent callers obtains the non-NULL
pointer and performs the put, the other gets NULL and skips it.

(cherry picked from commit 13238dc0ee4f9ab8dafa2cca7295736191ae2f42)

## References
- https://git.kernel.org/stable/c/2af8b200cae3fdd0e917ecc2753b28bb40c876c1
- https://git.kernel.org/stable/c/455d98ed527fc94eed90406f90ab2391464ca657
- https://git.kernel.org/stable/c/4c71fd099513bfa8acab529b626e1f0097b76061
- https://git.kernel.org/stable/c/70d3e622b10092fc483e28e57b4e8c49d9cc7f68
- https://git.kernel.org/stable/c/82034799c6c14b3104668878c3f3e5786f777126
- https://git.kernel.org/stable/c/8ce44d28a84fd5e053a88b04872a89d95c0779d4
- https://git.kernel.org/stable/c/a00e92bf6583d019a4fb2c2df7007e6c9b269ce7
- https://git.kernel.org/stable/c/ca3f48c3567dd49efdc55b80029ae74659c682ee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31656.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31656
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
