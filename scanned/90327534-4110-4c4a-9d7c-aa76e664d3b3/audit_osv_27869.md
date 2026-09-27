# [H] xhci: handle isoc Babble and Buffer Overrun events properly

## Summary
Severity: High
Advisory: CVE-2024-26659
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-02
Source: https://osv.dev/vulnerability/CVE-2024-26659
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.36 <5.10.213, >=5.11.0 <5.15.152, >=5.16.0 <6.1.82, >=6.2.0 <6.6.17, >=6.7.0 <6.7.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

xhci: handle isoc Babble and Buffer Overrun events properly

xHCI 4.9 explicitly forbids assuming that the xHC has released its
ownership of a multi-TRB TD when it reports an error on one of the
early TRBs. Yet the driver makes such assumption and releases the TD,
allowing the remaining TRBs to be freed or overwritten by new TDs.

The xHC should also report completion of the final TRB due to its IOC
flag being set by us, regardless of prior errors. This event cannot
be recognized if the TD has already been freed earlier, resulting in
"Transfer event TRB DMA ptr not part of current TD" error message.

Fix this by reusing the logic for processing isoc Transaction Errors.
This also handles hosts which fail to report the final completion.

Fix transfer length reporting on Babble errors. They may be caused by
device malfunction, no guarantee that the buffer has been filled.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/2aa7bcfdbb46241c701811bbc0d64d7884e3346c
- https://git.kernel.org/stable/c/2e3ec80ea7ba58bbb210e83b5a0afefee7c171d3
- https://git.kernel.org/stable/c/418456c0ce56209610523f21734c5612ee634134
- https://git.kernel.org/stable/c/696e4112e5c1ee61996198f0ebb6ca3fab55166e
- https://git.kernel.org/stable/c/7c4650ded49e5b88929ecbbb631efb8b0838e811
- https://git.kernel.org/stable/c/f5e7ffa9269a448a720e21f1ed1384d118298c97
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26659.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26659
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
