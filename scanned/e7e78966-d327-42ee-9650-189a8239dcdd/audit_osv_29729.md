# [M] i3c: mipi-i3c-hci: Mask ring interrupts before ring stop request

## Summary
Severity: Medium
Advisory: CVE-2024-45828
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-45828
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

i3c: mipi-i3c-hci: Mask ring interrupts before ring stop request

Bus cleanup path in DMA mode may trigger a RING_OP_STAT interrupt when
the ring is being stopped. Depending on timing between ring stop request
completion, interrupt handler removal and code execution this may lead
to a NULL pointer dereference in hci_dma_irq_handler() if it gets to run
after the io_data pointer is set to NULL in hci_dma_cleanup().

Prevent this my masking the ring interrupts before ring stop request.

## References
- https://git.kernel.org/stable/c/19cc5767334bfe980f52421627d0826c0da86721
- https://git.kernel.org/stable/c/6ca2738174e4ee44edb2ab2d86ce74f015a0cc32
- https://git.kernel.org/stable/c/9d745a56aea45e47f4755bc12e6429d6314dbb54
- https://git.kernel.org/stable/c/a6cddf68b3405b272b5a3cad9657be0b02b34bf4
- https://git.kernel.org/stable/c/a6dc4b4fda2e147e557050eaae51ff15edeb680b
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45828.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45828
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
