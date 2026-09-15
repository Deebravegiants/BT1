# [H] NFS: Automounted filesystems should inherit ro,noexec,nodev,sync flags

## Summary
Severity: High
Advisory: CVE-2025-68764
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-05
Source: https://osv.dev/vulnerability/CVE-2025-68764
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.63, >=6.13.0 <6.17.13, >=6.18.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFS: Automounted filesystems should inherit ro,noexec,nodev,sync flags

When a filesystem is being automounted, it needs to preserve the
user-set superblock mount options, such as the "ro" flag.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/4b296944e632cf4c6a4cc8e2585c6451eae47b1b
- https://git.kernel.org/stable/c/612cc98698d667df804792f0c47d4e501e66da29
- https://git.kernel.org/stable/c/8675c69816e4276b979ff475ee5fac4688f80125
- https://git.kernel.org/stable/c/a3dc6c40bcab1a888d5c0d134ccc0746b4c98929
- https://git.kernel.org/stable/c/ba1495aefd22fcf0746a2a3025c95d766d7cde4d
- https://git.kernel.org/stable/c/c09070b4def1b34e473a746c6a5331ccb80902c1
- https://git.kernel.org/stable/c/dce10c59211e5cd763a62ea01e79b82a629811e3
- https://git.kernel.org/stable/c/df9b003a2ecacc7218486fbb31fe008c93097d5f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68764.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68764
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
