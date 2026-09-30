# [H] perf: Ensure swevent hrtimer is properly destroyed

## Summary
Severity: High
Advisory: CVE-2026-23014
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-28
Source: https://osv.dev/vulnerability/CVE-2026-23014
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf: Ensure swevent hrtimer is properly destroyed

With the change to hrtimer_try_to_cancel() in
perf_swevent_cancel_hrtimer() it appears possible for the hrtimer to
still be active by the time the event gets freed.

Make sure the event does a full hrtimer_cancel() on the free path by
installing a perf_event::destroy handler.

## References
- https://git.kernel.org/stable/c/deee9dfb111ab00f9dfd46c0c7e36656b80f5235
- https://git.kernel.org/stable/c/ff5860f5088e9076ebcccf05a6ca709d5935cfa9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23014.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23014
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
