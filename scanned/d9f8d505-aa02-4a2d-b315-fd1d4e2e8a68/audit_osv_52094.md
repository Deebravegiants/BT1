# [M] CVE-2021-47064

## Summary
Severity: Medium
Advisory: CVE-2021-47064
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2021-47064
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mt76: fix potential DMA mapping leak

With buf uninitialized in mt76_dma_tx_queue_skb_raw, its field skip_unmap
could potentially inherit a non-zero value from stack garbage.
If this happens, it will cause DMA mappings for MCU command frames to not be
unmapped after completion

## References
- https://git.kernel.org/stable/c/91b9548d413fda488ea853cd1b9f59b572db3a0c
- https://git.kernel.org/stable/c/9b68ce2856dadc0e1cb6fd21fbeb850da49efd08
- https://git.kernel.org/stable/c/9fa26701cd1fc4d932d431971efc5746325bdfce
- https://git.kernel.org/stable/c/b4403cee6400c5f679e9c4a82b91d61aa961eccf
