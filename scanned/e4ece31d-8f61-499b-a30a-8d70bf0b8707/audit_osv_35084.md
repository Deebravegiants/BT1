# [H] hung_task: fix warnings caused by unaligned lock pointers

## Summary
Severity: High
Advisory: CVE-2025-68250
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68250
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.17.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

hung_task: fix warnings caused by unaligned lock pointers

The blocker tracking mechanism assumes that lock pointers are at least
4-byte aligned to use their lower bits for type encoding.

However, as reported by Eero Tamminen, some architectures like m68k
only guarantee 2-byte alignment of 32-bit values. This breaks the
assumption and causes two related WARN_ON_ONCE checks to trigger.

To fix this, the runtime checks are adjusted to silently ignore any lock
that is not 4-byte aligned, effectively disabling the feature in such
cases and avoiding the related warnings.

Thanks to Geert Uytterhoeven for bisecting!

## References
- https://git.kernel.org/stable/c/c0e2dcbe54cb15ecdf9d8f4501c6720423243888
- https://git.kernel.org/stable/c/c97513cddcfc235f2522617980838e500af21d01
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68250.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68250
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
