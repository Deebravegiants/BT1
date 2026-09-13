# [H] netfilter: nf_conncount: update last_gc only when GC has been performed

## Summary
Severity: High
Advisory: CVE-2026-23139
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2026-23139
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.161, >=6.2.0 <6.6.121, >=6.7.0 <6.12.66, >=6.13.0 <6.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_conncount: update last_gc only when GC has been performed

Currently last_gc is being updated everytime a new connection is
tracked, that means that it is updated even if a GC wasn't performed.
With a sufficiently high packet rate, it is possible to always bypass
the GC, causing the list to grow infinitely.

Update the last_gc value only when a GC has been actually performed.

## References
- https://git.kernel.org/stable/c/26a82dce2beee39c43c109d9647e16f49cb02a35
- https://git.kernel.org/stable/c/2c7c71113ed6d3e2f3aca4c088f22283016ff34f
- https://git.kernel.org/stable/c/3cd717359e56f82f06cbf8279b47a7d79880c6f3
- https://git.kernel.org/stable/c/7811ba452402d58628e68faedf38745b3d485e3c
- https://git.kernel.org/stable/c/8bdafdf4900040a81422056cabe5e00a37bd101a
- https://git.kernel.org/stable/c/9f45588993d7f115280fc726119ca86fba32a811
- https://git.kernel.org/stable/c/c4cde57c8affdcca5bcff53a1047e15d268bdca1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23139.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23139
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
