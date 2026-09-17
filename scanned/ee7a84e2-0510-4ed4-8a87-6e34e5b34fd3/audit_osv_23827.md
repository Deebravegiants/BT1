# [M] ipw2x00: Fix potential NULL dereference in libipw_xmit()

## Summary
Severity: Medium
Advisory: CVE-2022-49544
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49544
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.15 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipw2x00: Fix potential NULL dereference in libipw_xmit()

crypt and crypt->ops could be null, so we need to checking null
before dereference

## References
- https://git.kernel.org/stable/c/167affc11781d7d35c4c3a7630a549ac74dd0b21
- https://git.kernel.org/stable/c/1ff6b0727c8988f25eeb670b6c038c1120bb58dd
- https://git.kernel.org/stable/c/48d4a820fd33f012e5f63735a59d15b5a3882882
- https://git.kernel.org/stable/c/528d2023ccf4748fd542582955236c1634a7d293
- https://git.kernel.org/stable/c/5f7ea274e88c0eeffe6bd6dbf6cf5c479d356af6
- https://git.kernel.org/stable/c/8fb1b9beb085bb767ae43e441db5ac6fcd66a04d
- https://git.kernel.org/stable/c/98d1dc32f890642476dbb78ed3437a456bf421b0
- https://git.kernel.org/stable/c/b4628e0d3754ab2fc98ee6e3d21851ba45798077
- https://git.kernel.org/stable/c/e8366bbabe1d207cf7c5b11ae50e223ae6fc278b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49544.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49544
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
