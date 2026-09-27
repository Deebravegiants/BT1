# [H] af_unix: Set gc_in_progress to true in unix_gc().

## Summary
Severity: High
Advisory: CVE-2026-53361
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-07-04
Source: https://osv.dev/vulnerability/CVE-2026-53361
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.183, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.9.0 <6.18.38

## Details
In the Linux kernel, the following vulnerability has been resolved:

af_unix: Set gc_in_progress to true in unix_gc().

Igor Ushakov reported that unix_gc() could run with gc_in_progress
being false if the work is scheduled while running:

  Thread 1         Thread 2                     Thread 3
  --------         --------                     --------
                   unix_schedule_gc()           unix_schedule_gc()
                   `- if (!gc_in_progress)      `- if (!gc_in_progress)
                      |- gc_in_progress = true     |
                      `- queue_work()              |
  unix_gc() <----------------/                     |
  |                                                |- gc_in_progress = true
  ...                                              `- queue_work()
  |                                                       |
  `- gc_in_progress = false                               |
                                                          |
  unix_gc() <---------------------------------------------'
  |
  ... /* gc_in_progress == false */
  |
  `- gc_in_progress = false

unix_peek_fpl() relies on gc_in_progress not to confuse GC
by MSG_PEEK.

Let's set gc_in_progress to true in unix_gc().

## References
- https://git.kernel.org/stable/c/0cfa78c050662784fc8e3ab26dbfd1dc632b2082
- https://git.kernel.org/stable/c/20aa894d475bd8086b25c1113ec4ca70f70c7a98
- https://git.kernel.org/stable/c/591f1ac217428a6d2b32a8ac14aac0fab44f155a
- https://git.kernel.org/stable/c/82c17e13d404f686e164590483fd6c1abaa675d0
- https://git.kernel.org/stable/c/d82ba05263c69fa2437fe93e4e561cc40f4c03af
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53361.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53361
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
