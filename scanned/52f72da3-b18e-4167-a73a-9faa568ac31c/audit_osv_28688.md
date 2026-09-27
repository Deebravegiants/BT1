# [H] bpf: Protect against int overflow for stack access size

## Summary
Severity: High
Advisory: CVE-2024-35905
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35905
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.85, >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Protect against int overflow for stack access size

This patch re-introduces protection against the size of access to stack
memory being negative; the access size can appear negative as a result
of overflowing its signed int representation. This should not actually
happen, as there are other protections along the way, but we should
protect against it anyway. One code path was missing such protections
(fixed in the previous patch in the series), causing out-of-bounds array
accesses in check_stack_range_initialized(). This patch causes the
verification of a program with such a non-sensical access size to fail.

This check used to exist in a more indirect way, but was inadvertendly
removed in a833a17aeac7.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/203a68151e8eeb331d4a64ab78303f3a15faf103
- https://git.kernel.org/stable/c/37dc1718dc0c4392dbfcb9adec22a776e745dd69
- https://git.kernel.org/stable/c/3f0784b2f1eb9147973d8c43ba085c5fdf44ff69
- https://git.kernel.org/stable/c/98cdac206b112bec63852e94802791e316acc2c1
- https://git.kernel.org/stable/c/9970e059af471478455f9534e8c3db82f8c5496d
- https://git.kernel.org/stable/c/ecc6a2101840177e57c925c102d2d29f260d37c8
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35905.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35905
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
