# [H] virt: sev-guest: Explicitly leak pages in unknown state

## Summary
Severity: High
Advisory: CVE-2026-64104
Ecosystem: Linux
CVSS: 8.7 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64104
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

virt: sev-guest: Explicitly leak pages in unknown state

When set_memory_{encrypted,decrypted}() fail, the user cannot know at which
point the function failed, meaning that the pages are left in an unknown state
from the point of view of the caller.

Since the pages may be left in an unencrypted state, they are not suitable for
general use, and cannot be returned safely to the buddy allocator. Avoid the
issue by never freeing the pages, and then do the proper accounting by calling
snp_leak_pages().

## References
- https://git.kernel.org/stable/c/3d0cd0065deeb054b4b29236432e851806b7cc81
- https://git.kernel.org/stable/c/bee400ad4f4259c9c0758e4f1960a1eed6f6f9f0
- https://git.kernel.org/stable/c/fd948c3f96b18ff9ba7d3e8eae13d196593e1aaf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64104.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64104
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
