# [M] media: pci: tw68: Fix null-ptr-deref bug in buf prepare and finish

## Summary
Severity: Medium
Advisory: CVE-2023-53244
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53244
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: pci: tw68: Fix null-ptr-deref bug in buf prepare and finish

When the driver calls tw68_risc_buffer() to prepare the buffer, the
function call dma_alloc_coherent may fail, resulting in a empty buffer
buf->cpu. Later when we free the buffer or access the buffer, null ptr
deref is triggered.

This bug is similar to the following one:
https://git.linuxtv.org/media_stage.git/commit/?id=2b064d91440b33fba5b452f2d1b31f13ae911d71.

We believe the bug can be also dynamically triggered from user side.
Similarly, we fix this by checking the return value of tw68_risc_buffer()
and the value of buf->cpu before buffer free.

## References
- https://git.kernel.org/stable/c/1634b7adcc5bef645b3666fdd564e5952a9e24e0
- https://git.kernel.org/stable/c/3715c5e9a8f96b6ed0dcbea06da443efccac1ecc
- https://git.kernel.org/stable/c/3c67f49a6643d973e83968ea35806c7b5ae68b56
- https://git.kernel.org/stable/c/dcf632bca424e6ff8c8eb89c96694e7f05cd29b6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53244.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53244
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
