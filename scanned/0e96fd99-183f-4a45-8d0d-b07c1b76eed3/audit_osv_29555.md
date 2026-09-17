# [H] media: pci: ivtv: Add check for DMA map result

## Summary
Severity: High
Advisory: CVE-2024-43877
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-21
Source: https://osv.dev/vulnerability/CVE-2024-43877
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: pci: ivtv: Add check for DMA map result

In case DMA fails, 'dma->SG_length' is 0. This value is later used to
access 'dma->SGarray[dma->SG_length - 1]', which will cause out of
bounds access.

Add check to return early on invalid value. Adjust warnings accordingly.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/24062aa7407091dee3e45a8e8037df437e848718
- https://git.kernel.org/stable/c/38f72c7e7c6b55614f9407555fd5ce9d019b0fa4
- https://git.kernel.org/stable/c/3d8fd92939e21ff0d45100ab208f8124af79402a
- https://git.kernel.org/stable/c/629913d6d79508b166c66e07e4857e20233d85a9
- https://git.kernel.org/stable/c/81d0664bed91a858c7b50c263954b59d65f1b414
- https://git.kernel.org/stable/c/c766065e8272085ea9c436414b7ddf1f12e7787b
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43877.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43877
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
