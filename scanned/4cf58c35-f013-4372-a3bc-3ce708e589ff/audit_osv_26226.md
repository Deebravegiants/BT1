# [M] x86/mm, kexec, ima: Use memblock_free_late() from ima_free_kexec_buffer()

## Summary
Severity: Medium
Advisory: CVE-2023-52576
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52576
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <6.1.56, >=6.2.0 <6.5.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/mm, kexec, ima: Use memblock_free_late() from ima_free_kexec_buffer()

The code calling ima_free_kexec_buffer() runs long after the memblock
allocator has already been torn down, potentially resulting in a use
after free in memblock_isolate_range().

With KASAN or KFENCE, this use after free will result in a BUG
from the idle task, and a subsequent kernel panic.

Switch ima_free_kexec_buffer() over to memblock_free_late() to avoid
that bug.

## References
- https://git.kernel.org/stable/c/34cf99c250d5cd2530b93a57b0de31d3aaf8685b
- https://git.kernel.org/stable/c/d2dfbc0e3b7a04c2d941421a958dc31c897fb204
- https://git.kernel.org/stable/c/eef16bfdb212da60f5144689f2967fb25b051a2b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52576.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52576
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
