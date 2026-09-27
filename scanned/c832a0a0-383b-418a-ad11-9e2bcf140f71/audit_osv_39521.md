# [H] net: rds: fix MR cleanup on copy error

## Summary
Severity: High
Advisory: CVE-2026-46053
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46053
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: rds: fix MR cleanup on copy error

__rds_rdma_map() hands sg/pages ownership to the transport after
get_mr() succeeds. If copying the generated cookie back to user space
fails after that point, the error path must not free those resources
again before dropping the MR reference.

Remove the duplicate unpin/free from the put_user() failure branch so
that MR teardown is handled only through the existing final cleanup
path.

## References
- https://git.kernel.org/stable/c/033370ffb3c9c0264d19f8ba9ef769523266589a
- https://git.kernel.org/stable/c/106dc689206610cfa2098f593fdd1e020c997835
- https://git.kernel.org/stable/c/8141a2dc70080eda1aedc0389ed2db2b292af5bd
- https://git.kernel.org/stable/c/8fdbb6262a4a3ed44a0830a7793903b54bb27bdc
- https://git.kernel.org/stable/c/91a44b406bc1f9e1c5da0cb7d0d5991b43b79147
- https://git.kernel.org/stable/c/b3cb8cae530b2727d8245684148bb49425f6765c
- https://git.kernel.org/stable/c/d95cea9298be1ba8876e3f156be96d3a492085ca
- https://git.kernel.org/stable/c/ec55a86f7fba7d9111df94b9c11a4755ed492995
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46053.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46053
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
