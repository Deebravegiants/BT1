# [H] fbdev: core: Fix pointer desynchronization in fb_io_read()

## Summary
Severity: High
Advisory: CVE-2026-80578
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80578
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev: core: Fix pointer desynchronization in fb_io_read()

In fb_io_read(), if copy_to_user() performs a partial copy (e.g., due to
a faulty user buffer), the loop adjusts the chunk size 'c' and updates
the remaining 'count'. However, the hardware 'src' pointer has already
been eagerly advanced by the original chunk size.

If the loop is allowed to continue, the read will resume from an
incorrect, over-advanced offset. Since the remaining 'count' was only
decremented by the successful bytes, this desynchronization causes the
next iterations to execute more hardware reads than originally bounded,
eventually leading to out-of-bounds I/O reads.

Fix this by breaking out of the loop immediately upon a partial
copy_to_user(). A partial copy indicates a faulty user buffer, making
subsequent read attempts futile. Breaking out ensures we return the
number of successfully read bytes without risking out-of-bounds hardware
accesses in subsequent mismatched iterations.

## References
- https://git.kernel.org/stable/c/42a6d8126c194133eafab2b0fd5c8668ebfcba5b
- https://git.kernel.org/stable/c/42bc07b4e5a3c8a02a433388f562a8f46d093e11
- https://git.kernel.org/stable/c/7110b7b794a2aac2c5cf8eb06ebf2af724c74d50
- https://git.kernel.org/stable/c/7ff87a01ae3a8cd0208f7499386998223a8b5dba
- https://git.kernel.org/stable/c/81cc73be40c6f028f1ee3f438ace46afe666dbae
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80578.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80578
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
