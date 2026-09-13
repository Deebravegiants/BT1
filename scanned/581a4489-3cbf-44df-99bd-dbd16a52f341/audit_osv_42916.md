# [H] dmaengine: sh: rz-dmac: Move interrupt request after everything is set up

## Summary
Severity: High
Advisory: CVE-2026-72146
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72146
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: sh: rz-dmac: Move interrupt request after everything is set up

Once the interrupt is requested, the interrupt handler may run immediately.
Since the IRQ handler can access channel->ch_base, which is initialized
only after requesting the IRQ, this may lead to invalid memory access.
Likewise, the IRQ thread may access uninitialized data (the ld_free,
ld_queue, and ld_active lists), which may also lead to issues.

Request the interrupts only after everything is set up. To keep the error
path simpler, use dmam_alloc_coherent() instead of dma_alloc_coherent().

## References
- https://git.kernel.org/stable/c/07ae600bd353b22f31a8f1007269744fafc7f123
- https://git.kernel.org/stable/c/0e0c5b3cf374ebf3c589741751e1fbc67f53ec2f
- https://git.kernel.org/stable/c/2a4d9e2234c3f817bb0ddbc8680d09ce9be84f93
- https://git.kernel.org/stable/c/5b12de6229d662864ee22c11d4876652b40120f0
- https://git.kernel.org/stable/c/731712403ddb39d1a76a11abf339a0615bc85de7
- https://git.kernel.org/stable/c/d24d53323e817d79a4bd111bd10b34dbc96e64a8
- https://git.kernel.org/stable/c/ec9f66c91bffdb69d309bae6dfb387562db7ebc8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72146.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72146
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
