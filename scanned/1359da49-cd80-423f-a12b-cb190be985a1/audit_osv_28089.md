# [H] cpumap: Zero-initialise xdp_rxq_info struct before running XDP program

## Summary
Severity: High
Advisory: CVE-2024-27431
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-27431
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.213, >=5.11.0 <5.15.152, >=5.16.0 <6.1.82, >=6.2.0 <6.6.22, >=6.7.0 <6.7.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

cpumap: Zero-initialise xdp_rxq_info struct before running XDP program

When running an XDP program that is attached to a cpumap entry, we don't
initialise the xdp_rxq_info data structure being used in the xdp_buff
that backs the XDP program invocation. Tobias noticed that this leads to
random values being returned as the xdp_md->rx_queue_index value for XDP
programs running in a cpumap.

This means we're basically returning the contents of the uninitialised
memory, which is bad. Fix this by zero-initialising the rxq data
structure before running the XDP program.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/2487007aa3b9fafbd2cb14068f49791ce1d7ede5
- https://git.kernel.org/stable/c/3420b3ff1ff489c177ea1cb7bd9fbbc4e9a0be95
- https://git.kernel.org/stable/c/5f4e51abfbe6eb444fa91906a5cd083044278297
- https://git.kernel.org/stable/c/eaa7cb836659ced2d9f814ac32aa3ec193803ed6
- https://git.kernel.org/stable/c/f0363af9619c77730764f10360e36c6445c12f7b
- https://git.kernel.org/stable/c/f562e4c4aab00986dde3093c4be919c3f2b85a4a
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27431.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27431
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
