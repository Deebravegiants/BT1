# [M] x86/resctrl: Fix allocation of cleanest CLOSID on platforms with no monitors

## Summary
Severity: Medium
Advisory: CVE-2025-38049
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-38049
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/resctrl: Fix allocation of cleanest CLOSID on platforms with no monitors

Commit

  6eac36bb9eb0 ("x86/resctrl: Allocate the cleanest CLOSID by searching closid_num_dirty_rmid")

added logic that causes resctrl to search for the CLOSID with the fewest dirty
cache lines when creating a new control group, if requested by the arch code.
This depends on the values read from the llc_occupancy counters. The logic is
applicable to architectures where the CLOSID effectively forms part of the
monitoring identifier and so do not allow complete freedom to choose an unused
monitoring identifier for a given CLOSID.

This support missed that some platforms may not have these counters.  This
causes a NULL pointer dereference when creating a new control group as the
array was not allocated by dom_data_init().

As this feature isn't necessary on platforms that don't have cache occupancy
monitors, add this to the check that occurs when a new control group is
allocated.

## References
- https://git.kernel.org/stable/c/93a418fc61da13d1ee4047d4d1327990f7a2816a
- https://git.kernel.org/stable/c/a121798ae669351ec0697c94f71c3a692b2a755b
- https://git.kernel.org/stable/c/a8a1bcc27d4607227088d80483164289b5348293
- https://git.kernel.org/stable/c/ed5addb55e403ad6598102bcf546e068ae01fef6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38049.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38049
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
