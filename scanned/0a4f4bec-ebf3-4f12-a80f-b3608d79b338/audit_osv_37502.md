# [H] iommupt: Fix short gather if the unmap goes into a large mapping

## Summary
Severity: High
Advisory: CVE-2026-31735
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31735
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommupt: Fix short gather if the unmap goes into a large mapping

unmap has the odd behavior that it can unmap more than requested if the
ending point lands within the middle of a large or contiguous IOPTE.

In this case the gather should flush everything unmapped which can be
larger than what was requested to be unmapped. The gather was only
flushing the range requested to be unmapped, not extending to the extra
range, resulting in a short invalidation if the caller hits this special
condition.

This was found by the new invalidation/gather test I am adding in
preparation for ARMv8. Claude deduced the root cause.

As far as I remember nothing relies on unmapping a large entry, so this is
likely not a triggerable bug.

## References
- https://git.kernel.org/stable/c/50ecd96a28f712f8b682c0441f4cb9b086d28816
- https://git.kernel.org/stable/c/ee6e69d032550687a3422504bfca3f834c7b5061
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31735.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31735
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
