# [H] scsi: ufs: bsg: Set bsg_queue to NULL after removal

## Summary
Severity: High
Advisory: CVE-2024-54458
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-54458
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.129, >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: ufs: bsg: Set bsg_queue to NULL after removal

Currently, this does not cause any issues, but I believe it is necessary to
set bsg_queue to NULL after removing it to prevent potential use-after-free
(UAF) access.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/1e95c798d8a7f70965f0f88d4657b682ff0ec75f
- https://git.kernel.org/stable/c/22018622e1e9e371198dbd983af946a844d5924c
- https://git.kernel.org/stable/c/5e7b6e44468c3242c21c2a8656d009fb3eb50a73
- https://git.kernel.org/stable/c/5f782d4741bf558def60df192b858b0efc6a5f0a
- https://git.kernel.org/stable/c/88a01e9c9ad40c075756ba93b47984461d4ff15d
- https://git.kernel.org/stable/c/9193bdc170cc23fe98aca71d1a63c0bf6e1e853b
- https://git.kernel.org/stable/c/bb4783c670180b922267222408e1c48d22dfbb46
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/54xxx/CVE-2024-54458.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-54458
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
