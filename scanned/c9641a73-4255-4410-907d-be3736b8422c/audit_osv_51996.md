# [M] CVE-2021-46939

## Summary
Severity: Medium
Advisory: CVE-2021-46939
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46939
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing: Restructure trace_clock_global() to never block

It was reported that a fix to the ring buffer recursion detection would
cause a hung machine when performing suspend / resume testing. The
following backtrace was extracted from debugging that case:

Call Trace:
 trace_clock_global+0x91/0xa0
 __rb_reserve_next+0x237/0x460
 ring_buffer_lock_reserve+0x12a/0x3f0
 trace_buffer_lock_reserve+0x10/0x50
 __trace_graph_return+0x1f/0x80
 trace_graph_return+0xb7/0xf0
 ? trace_clock_global+0x91/0xa0
 ftrace_return_to_handler+0x8b/0xf0
 ? pv_hash+0xa0/0xa0
 return_to_handler+0x15/0x30
 ? ftrace_graph_caller+0xa0/0xa0
 ? trace_clock_global+0x91/0xa0
 ? __rb_reserve_next+0x237/0x460
 ? ring_buffer_lock_reserve+0x12a/0x3f0
 ? trace_event_buffer_lock_reserve+0x3c/0x120
 ? trace_event_buffer_reserve+0x6b/0xc0
 ? trace_event_raw_event_device_pm_callback_start+0x125/0x2d0
 ? dpm_run_callback+0x3b/0xc0
 ? pm_ops_is_empty+0x50/0x50
 ? platform_get_irq_byname_optional+0x90/0x90
 ? trace_device_pm_callback_start+0x82/0xd0
 ? dpm_run_callback+0x49/0xc0

With the following RIP:

RIP: 0010:native_queued_spin_lock_slowpath+0x69/0x200

Since the fix to the recursion detection would allow a single recursion to
happen while tracing, this lead to the trace_clock_global() taking a spin
lock and then trying to take it again:

ring_buffer_lock_reserve() {
  trace_clock_global() {
    arch_spin_lock() {
      queued_spin_lock_slowpath() {
        /* lock taken */
        (something else gets traced by function graph tracer)
          ring_buffer_lock_reserve() {
            trace_clock_global() {
              arch_spin_lock() {
                queued_spin_lock_slowpath() {
                /* DEAD LOCK! */

Tracing should *never* block, as it can lead to strange lockups like the
above.

Restructure the trace_clock_global() code to instead of simply taking a
lock to update the recorded "prev_time" simply use it, as two events
happening on two different CPUs that calls this at the same time, really
doesn't matter which one goes first. Use a trylock to grab the lock for
updating the prev_time, and if it fails, simply try again the next time.
If it failed to be taken, that means something else is already updating
it.


Bugzilla: https://bugzilla.kernel.org/show_bug.cgi?id=212761

## References
- https://git.kernel.org/stable/c/d43d56dbf452ccecc1ec735cd4b6840118005d7c
- https://git.kernel.org/stable/c/6e2418576228eeb12e7ba82edb8f9500623942ff
- https://git.kernel.org/stable/c/859b47a43f5a0e5b9a92b621dc6ceaad39fb5c8b
- https://git.kernel.org/stable/c/91ca6f6a91f679c8645d7f3307e03ce86ad518c4
- https://git.kernel.org/stable/c/a33614d52e97fc8077eb0b292189ca7d964cc534
- https://git.kernel.org/stable/c/aafe104aa9096827a429bc1358f8260ee565b7cc
- https://git.kernel.org/stable/c/1fca00920327be96f3318224f502e4d5460f9545
- https://git.kernel.org/stable/c/2a1bd74b8186d7938bf004f5603f25b84785f63e
- https://git.kernel.org/stable/c/c64da3294a7d59a4bf6874c664c13be892f15f44
