# [M] ASoC: fsl: Fix refcount leak in imx_sgtl5000_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49486
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49486
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: fsl: Fix refcount leak in imx_sgtl5000_probe

of_find_i2c_device_by_node() takes a reference,
In error paths, we should call put_device() to drop
the reference to aviod refount leak.

## References
- https://git.kernel.org/stable/c/41cd312dfe980af869c3503b4d38e62ed20dd3b7
- https://git.kernel.org/stable/c/4bfbbfdb3d761323127a67d7d765abe2f77d7b21
- https://git.kernel.org/stable/c/7f75e9f629ef54a0845b43889d8ab9dd6e280dd5
- https://git.kernel.org/stable/c/922bccdb1796a9e7b989f2bc6d9ada7b499a4329
- https://git.kernel.org/stable/c/96fc3da6184af5687e153d420cd7dcdeefdd2f9a
- https://git.kernel.org/stable/c/e84aaf23ca82753d765bf84d05295d9d9c5fed29
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49486.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49486
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
