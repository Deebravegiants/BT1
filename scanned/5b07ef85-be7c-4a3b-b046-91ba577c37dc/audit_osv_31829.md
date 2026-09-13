# [M] nfp: bpf: Add check for nfp_app_ctrl_msg_alloc()

## Summary
Severity: Medium
Advisory: CVE-2025-21848
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2025-21848
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.130, >=6.2.0 <6.6.80, >=6.7.0 <6.12.17, >=6.13.0 <6.13.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfp: bpf: Add check for nfp_app_ctrl_msg_alloc()

Add check for the return value of nfp_app_ctrl_msg_alloc() in
nfp_bpf_cmsg_alloc() to prevent null pointer dereference.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/1358d8e07afdf21d49ca6f00c56048442977e00a
- https://git.kernel.org/stable/c/29ccb1e4040da6ff02b7e64efaa2f8e6bf06020d
- https://git.kernel.org/stable/c/878e7b11736e062514e58f3b445ff343e6705537
- https://git.kernel.org/stable/c/897c32cd763fd11d0b6ed024c52f44d2475bb820
- https://git.kernel.org/stable/c/924b239f9704566e0d86abd894d2d64bd73c11eb
- https://git.kernel.org/stable/c/bd97f60750bb581f07051f98e31dfda59d3a783b
- https://git.kernel.org/stable/c/d64c6ca420019712e194fe095b55f87363e22a9a
- https://git.kernel.org/stable/c/e976ea6c5e1b005c64467cbf94a8577aae9c7d81
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21848.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21848
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
