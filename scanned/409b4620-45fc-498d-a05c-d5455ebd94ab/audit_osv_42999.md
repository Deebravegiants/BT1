# [H] net: qrtr: fix 32-bit integer overflow in qrtr_endpoint_post()

## Summary
Severity: High
Advisory: CVE-2026-72298
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72298
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.261, >=5.11.0 <5.15.212, >=5.13.0 <6.1.178, >=5.16.0 <6.6.145, >=6.2.0 <6.12.97, >=6.7.0 <6.18.40, >=6.13.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: qrtr: fix 32-bit integer overflow in qrtr_endpoint_post()

qrtr_endpoint_post() validates an incoming packet with

	if (!size || len != ALIGN(size, 4) + hdrlen)
		goto err;

where size comes from the wire. On 32-bit, size_t is 32 bits and
ALIGN(size, 4) wraps to 0 for size >= 0xfffffffd, so the check
passes and skb_put_data(skb, data + hdrlen, size) writes past the
hdrlen-sized skb and oopses the kernel. 64-bit is unaffected.

This is the 32-bit residual of ad9d24c9429e2 ("net: qrtr: fix OOB
Read in qrtr_endpoint_post"), which fixed only the 64-bit case.

Reject any size that cannot fit the buffer before the ALIGN.

## References
- https://git.kernel.org/stable/c/20054869770c7df060c5ecee3e8bbf9029c47191
- https://git.kernel.org/stable/c/22100a8f73d4ae4f17697dae93d4e2e1d283a6ec
- https://git.kernel.org/stable/c/242408b5b763c01288adf3113cbce84378a76e1a
- https://git.kernel.org/stable/c/3665e644ea081c4624a1637023b0de3b29f4ae04
- https://git.kernel.org/stable/c/689b7267f8632b4661879dc323e26ebb60978afb
- https://git.kernel.org/stable/c/7f72c285f6d3bf63968a0344beee8ab1b370198b
- https://git.kernel.org/stable/c/b609f7f46916c6b05585ca82455077198a23770f
- https://git.kernel.org/stable/c/d0597074e99731fdad5593e4f6d056a3866f2cab
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72298.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72298
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
