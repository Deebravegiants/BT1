# [C] net: libwx: fix the using of Rx buffer DMA

## Summary
Severity: Critical
Advisory: CVE-2025-38533
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38533
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.100, >=6.7.0 <6.12.40, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: libwx: fix the using of Rx buffer DMA

The wx_rx_buffer structure contained two DMA address fields: 'dma' and
'page_dma'. However, only 'page_dma' was actually initialized and used
to program the Rx descriptor. But 'dma' was uninitialized and used in
some paths.

This could lead to undefined behavior, including DMA errors or
use-after-free, if the uninitialized 'dma' was used. Althrough such
error has not yet occurred, it is worth fixing in the code.

## References
- https://git.kernel.org/stable/c/027701180a7bcb64c42eab291133ef0c87b5b6c5
- https://git.kernel.org/stable/c/05c37b574997892a40a0e9b9b88a481566b2367d
- https://git.kernel.org/stable/c/5fd77cc6bd9b368431a815a780e407b7781bcca0
- https://git.kernel.org/stable/c/ba7c793f96c1c2b944bb6f423d7243f3afc30fe9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38533.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38533
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
