# [H] caif: fix integer underflow in cffrml_receive()

## Summary
Severity: High
Advisory: CVE-2025-68799
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-68799
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

caif: fix integer underflow in cffrml_receive()

The cffrml_receive() function extracts a length field from the packet
header and, when FCS is disabled, subtracts 2 from this length without
validating that len >= 2.

If an attacker sends a malicious packet with a length field of 0 or 1
to an interface with FCS disabled, the subtraction causes an integer
underflow.

This can lead to memory exhaustion and kernel instability, potential
information disclosure if padding contains uninitialized kernel memory.

Fix this by validating that len >= 2 before performing the subtraction.

## References
- https://git.kernel.org/stable/c/21fdcc00656a60af3c7aae2dea8dd96abd35519c
- https://git.kernel.org/stable/c/4ec29714aa4e0601ea29d2f02b461fc0ac92c2c3
- https://git.kernel.org/stable/c/785c7be6361630070790f6235b696da156ac71b3
- https://git.kernel.org/stable/c/8a11ff0948b5ad09b71896b7ccc850625f9878d1
- https://git.kernel.org/stable/c/c54091eec6fed19e94182aa05dd6846600a642f7
- https://git.kernel.org/stable/c/f407f1c9f45bbf5c99fd80b3f3f4a94fdbe35691
- https://git.kernel.org/stable/c/f818cd472565f8b0c2c409b040e0121c5cf8592c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68799.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68799
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
