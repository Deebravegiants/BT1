# [H] perf: Avoid undefined behavior from stopping/starting inactive events

## Summary
Severity: High
Advisory: CVE-2025-39821
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-39821
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf: Avoid undefined behavior from stopping/starting inactive events

Calling pmu->start()/stop() on perf events in PERF_EVENT_STATE_OFF can
leave event->hw.idx at -1. When PMU drivers later attempt to use this
negative index as a shift exponent in bitwise operations, it leads to UBSAN
shift-out-of-bounds reports.

The issue is a logical flaw in how event groups handle throttling when some
members are intentionally disabled. Based on the analysis and the
reproducer provided by Mark Rutland (this issue on both arm64 and x86-64).

The scenario unfolds as follows:

 1. A group leader event is configured with a very aggressive sampling
    period (e.g., sample_period = 1). This causes frequent interrupts and
    triggers the throttling mechanism.
 2. A child event in the same group is created in a disabled state
    (.disabled = 1). This event remains in PERF_EVENT_STATE_OFF.
    Since it hasn't been scheduled onto the PMU, its event->hw.idx remains
    initialized at -1.
 3. When throttling occurs, perf_event_throttle_group() and later
    perf_event_unthrottle_group() iterate through all siblings, including
    the disabled child event.
 4. perf_event_throttle()/unthrottle() are called on this inactive child
    event, which then call event->pmu->start()/stop().
 5. The PMU driver receives the event with hw.idx == -1 and attempts to
    use it as a shift exponent. e.g., in macros like PMCNTENSET(idx),
    leading to the UBSAN report.

The throttling mechanism attempts to start/stop events that are not
actively scheduled on the hardware.

Move the state check into perf_event_throttle()/perf_event_unthrottle() so
that inactive events are skipped entirely. This ensures only active events
with a valid hw.idx are processed, preventing undefined behavior and
silencing UBSAN warnings. The corrected check ensures true before
proceeding with PMU operations.

The problem can be reproduced with the syzkaller reproducer:

## References
- https://git.kernel.org/stable/c/b64fdd422a85025b5e91ead794db9d3ef970e369
- https://git.kernel.org/stable/c/d689135aa9c5e4e0eab5a92bbe35dab0c8d6677f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39821.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39821
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
