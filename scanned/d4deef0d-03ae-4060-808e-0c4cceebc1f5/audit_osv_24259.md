# [H] RDMA/siw: Fix immediate work request flush to completion queue

## Summary
Severity: High
Advisory: CVE-2022-50736
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2022-50736
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/siw: Fix immediate work request flush to completion queue

Correctly set send queue element opcode during immediate work request
flushing in post sendqueue operation, if the QP is in ERROR state.
An undefined ocode value results in out-of-bounds access to an array
for mapping the opcode between siw internal and RDMA core representation
in work completion generation. It resulted in a KASAN BUG report
of type 'global-out-of-bounds' during NFSoRDMA testing.

This patch further fixes a potential case of a malicious user which may
write undefined values for completion queue elements status or opcode,
if the CQ is memory mapped to user land. It avoids the same out-of-bounds
access to arrays for status and opcode mapping as described above.

## References
- https://git.kernel.org/stable/c/355d2eca68c10d713a42f68e62044b3d1c300471
- https://git.kernel.org/stable/c/6af043089d3f1210776d19b6fdabea610d4c7699
- https://git.kernel.org/stable/c/75af03fdf35acf15a3977f7115f6b8d10dff4bc7
- https://git.kernel.org/stable/c/bdf1da5df9da680589a7f74448dd0a94dd3e1446
- https://git.kernel.org/stable/c/f3d26a8589dfdeff328779b511f71fb90b10005e
- https://git.kernel.org/stable/c/f8d8fbd3b6d6cc3f25790cca5cffe8ded512fef6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50736.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50736
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
