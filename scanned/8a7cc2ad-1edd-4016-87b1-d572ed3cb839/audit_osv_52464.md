# [H] CVE-2021-47477

## Summary
Severity: High
Advisory: CVE-2021-47477
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47477
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

comedi: dt9812: fix DMA buffers on stack

USB transfer buffers are typically mapped for DMA and must not be
allocated on the stack or transfers will fail.

Allocate proper transfer buffers in the various command helpers and
return an error on short transfers instead of acting on random stack
data.

Note that this also fixes a stack info leak on systems where DMA is not
used as 32 bytes are always sent to the device regardless of how short
the command is.

## References
- https://git.kernel.org/stable/c/365a346cda82f51d835c49136a00a9df8a78c7f2
- https://git.kernel.org/stable/c/39ea61037ae78f14fa121228dd962ea3280eacf3
- https://git.kernel.org/stable/c/3ac273d154d634e2034508a14db82a95d7ad12ed
- https://git.kernel.org/stable/c/3efb7af8ac437085b6c776e5b54830b149d86efe
- https://git.kernel.org/stable/c/8a52bc480992c7c9da3ebfea456af731f50a4b97
- https://git.kernel.org/stable/c/a6af69768d5cb4b2528946d53be5fa19ade37723
- https://git.kernel.org/stable/c/20cebb8b620dc987e55ddc46801de986e081757e
- https://git.kernel.org/stable/c/536de747bc48262225889a533db6650731ab25d3
- https://git.kernel.org/stable/c/786f5b03450454557ff858a8bead5d7c0cbf78d6
