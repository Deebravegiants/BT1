# [H] rdma/cxgb4: Prevent potential integer overflow on 32bit

## Summary
Severity: High
Advisory: CVE-2024-57973
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-57973
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

rdma/cxgb4: Prevent potential integer overflow on 32bit

The "gl->tot_len" variable is controlled by the user.  It comes from
process_responses().  On 32bit systems, the "gl->tot_len + sizeof(struct
cpl_pass_accept_req) + sizeof(struct rss_header)" addition could have an
integer wrapping bug.  Use size_add() to prevent this.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/2b759f78b83221f4a1cae3aeb20b500e375f3ee6
- https://git.kernel.org/stable/c/4422f452d028850b9cc4fd8f1cf45a8ff91855eb
- https://git.kernel.org/stable/c/aeb814484387811b3579d5c78ad4eb301e3bf1c8
- https://git.kernel.org/stable/c/bd96a3935e89486304461a21752f824fc25e0f0b
- https://git.kernel.org/stable/c/d64148a10a85952352de6091ceed99fb9ce2d3ee
- https://git.kernel.org/stable/c/dd352107f22bfbecbbf3b74bde14f3f932296309
- https://git.kernel.org/stable/c/de8d88b68d0cfd41152a7a63d6aec0ed3e1b837a
- https://git.kernel.org/stable/c/e53ca458f543aa352d09b484550de173cb9085c2
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57973.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57973
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
