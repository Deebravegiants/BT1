# [H] accel/ethosu: fix arithmetic issues in dma_length()

## Summary
Severity: High
Advisory: CVE-2026-53171
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53171
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/ethosu: fix arithmetic issues in dma_length()

dma_length() derives DMA region usage from command stream values and
updates region_size[]:

    len = ((len + stride[0]) * size0 + stride[1]) * size1
    region_size[region] = max(..., len + dma->offset)

Several arithmetic issues can corrupt the derived region size:

- signed stride values may underflow when added to len
- intermediate multiplications may overflow
- len + dma->offset may overflow during region_size updates
- dma_length() error returns were not validated by the caller

region_size[] is later used by ethosu_job.c to validate command stream
accesses against GEM buffer sizes. Arithmetic wraparound can therefore
under-report region usage and bypass the bounds validation.

Fix by validating signed additions, using overflow helpers for
multiplications and offset updates, and propagating dma_length()
failures to the caller.

## References
- https://git.kernel.org/stable/c/6bb73845d1855ceaf50e397175e5979a7bdf69bc
- https://git.kernel.org/stable/c/ee6d9b6e51626f259c6f0e38d94f91be4fd14754
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53171.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53171
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
