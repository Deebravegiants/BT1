# [H] sctp: fix a potential overflow in sctp_ifwdtsn_skip

## Summary
Severity: High
Advisory: CVE-2023-53372
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53372
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <4.19.281, >=4.20.0 <5.4.241, >=5.5.0 <5.10.178, >=5.11.0 <5.15.108, >=5.16.0 <6.1.25, >=6.2.0 <6.2.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: fix a potential overflow in sctp_ifwdtsn_skip

Currently, when traversing ifwdtsn skips with _sctp_walk_ifwdtsn, it only
checks the pos against the end of the chunk. However, the data left for
the last pos may be < sizeof(struct sctp_ifwdtsn_skip), and dereference
it as struct sctp_ifwdtsn_skip may cause coverflow.

This patch fixes it by checking the pos against "the end of the chunk -
sizeof(struct sctp_ifwdtsn_skip)" in sctp_ifwdtsn_skip, similar to
sctp_fwdtsn_skip.

## References
- https://git.kernel.org/stable/c/32832a2caf82663870126c5186cf8f86c8b2a649
- https://git.kernel.org/stable/c/4fbd094d4131a10d06a45d64158567052a35b3f4
- https://git.kernel.org/stable/c/5c9367ac5a22d71841bcd00130f9146c9b227d57
- https://git.kernel.org/stable/c/6109f5b13ce3e3e537db6f18976ec0e9118d1c6f
- https://git.kernel.org/stable/c/79b28f42214a3d0d6a8c514db3602260bd5d6cb5
- https://git.kernel.org/stable/c/ad831a7079c99c01e801764b53bc9997c2e9c0f7
- https://git.kernel.org/stable/c/ad988e9b5ff04607e624a459209e8c2d0c15fc73
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53372.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53372
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
