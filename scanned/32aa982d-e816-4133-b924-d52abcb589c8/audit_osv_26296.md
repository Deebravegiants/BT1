# [H] i3c: mipi-i3c-hci: Fix out of bounds access in hci_dma_irq_handler

## Summary
Severity: High
Advisory: CVE-2023-52766
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52766
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.15.140, >=5.16.0 <6.1.64, >=6.2.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

i3c: mipi-i3c-hci: Fix out of bounds access in hci_dma_irq_handler

Do not loop over ring headers in hci_dma_irq_handler() that are not
allocated and enabled in hci_dma_init(). Otherwise out of bounds access
will occur from rings->headers[i] access when i >= number of allocated
ring headers.

## References
- https://git.kernel.org/stable/c/45a832f989e520095429589d5b01b0c65da9b574
- https://git.kernel.org/stable/c/4c86cb2321bd9c72d3b945ce7f747961beda8e65
- https://git.kernel.org/stable/c/7c2b91b30d74d7c407118ad72502d4ca28af1af6
- https://git.kernel.org/stable/c/8be39f66915b40d26ea2c18ba84b5c3d5da6809b
- https://git.kernel.org/stable/c/d23ad76f240c0f597b7a9eb79905d246f27d40df
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52766.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52766
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
