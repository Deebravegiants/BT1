# [C] crypto: hisilicon/sec - fix the aead software fallback for engine

## Summary
Severity: Critical
Advisory: CVE-2022-49260
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49260
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: hisilicon/sec - fix the aead software fallback for engine

Due to the subreq pointer misuse the private context memory. The aead
soft crypto occasionally casues the OS panic as setting the 64K page.
Here is fix it.

## References
- https://git.kernel.org/stable/c/0a2a464f863187f97e96ebc6384c052cafd4a54c
- https://git.kernel.org/stable/c/40dba7c26e897c637e91312b35f664f1d4d0073c
- https://git.kernel.org/stable/c/5c1149e2abe0b7489300736b8277b45b113de67f
- https://git.kernel.org/stable/c/ef7b10f3cac7810ddcfd976304fd125aca33d144
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49260.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49260
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
