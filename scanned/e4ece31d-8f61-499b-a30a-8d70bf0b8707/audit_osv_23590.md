# [M] hwrng: cavium - fix NULL but dereferenced coccicheck error

## Summary
Severity: Medium
Advisory: CVE-2022-49177
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49177
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwrng: cavium - fix NULL but dereferenced coccicheck error

Fix following coccicheck warning:
./drivers/char/hw_random/cavium-rng-vf.c:182:17-20: ERROR:
pdev is NULL but dereferenced.

## References
- https://git.kernel.org/stable/c/e47b12f9415169eceda6770fcf45802e0c8d2a66
- https://git.kernel.org/stable/c/e6205ad58a7ac194abfb33897585b38687d797fa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49177.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49177
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
