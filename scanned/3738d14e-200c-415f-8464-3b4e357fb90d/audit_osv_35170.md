# [H] scsi: target: Reset t_task_cdb pointer in error case

## Summary
Severity: High
Advisory: CVE-2025-68782
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-68782
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: Reset t_task_cdb pointer in error case

If allocation of cmd->t_task_cdb fails, it remains NULL but is later
dereferenced in the 'err' path.

In case of error, reset NULL t_task_cdb value to point at the default
fixed-size buffer.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/0260ad551b0815eb788d47f32899fbcd65d6f128
- https://git.kernel.org/stable/c/0d36db68fdb8a3325386fd9523b67735f944e1f3
- https://git.kernel.org/stable/c/45fd86b444105c8bd07a763f58635c87e5dc7aea
- https://git.kernel.org/stable/c/5053eab38a4c4543522d0c320c639c56a8b59908
- https://git.kernel.org/stable/c/6cac97b12bdab04832e0416d049efcd0d48d303b
- https://git.kernel.org/stable/c/8727663ded659aad55eef21e3864ebf5a4796a96
- https://git.kernel.org/stable/c/8edbb9e371af186b4cf40819dab65fafe109df4d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68782.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68782
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
