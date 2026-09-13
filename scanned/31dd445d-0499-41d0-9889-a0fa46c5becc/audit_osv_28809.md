# [H] Bluetooth: qca: add missing firmware sanity checks

## Summary
Severity: High
Advisory: CVE-2024-36880
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36880
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <5.15.159, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: qca: add missing firmware sanity checks

Add the missing sanity checks when parsing the firmware files before
downloading them to avoid accessing and corrupting memory beyond the
vmalloced buffer.

## References
- https://git.kernel.org/stable/c/02f05ed44b71152d5e11d29be28aed91c0489b4e
- https://git.kernel.org/stable/c/1caceadfb50432dbf6d808796cb6c34ebb6d662c
- https://git.kernel.org/stable/c/2e4edfa1e2bd821a317e7d006517dcf2f3fac68d
- https://git.kernel.org/stable/c/427281f9498ed614f9aabc80e46ec077c487da6d
- https://git.kernel.org/stable/c/ed53949cc92e28aaa3463d246942bda1fbb7f307
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36880.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36880
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
