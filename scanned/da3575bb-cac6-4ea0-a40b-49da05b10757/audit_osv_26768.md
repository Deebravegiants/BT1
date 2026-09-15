# [H] f2fs: synchronize atomic write aborts

## Summary
Severity: High
Advisory: CVE-2023-53838
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53838
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: synchronize atomic write aborts

To fix a race condition between atomic write aborts, I use the inode
lock and make COW inode to be re-usable thoroughout the whole
atomic file inode lifetime.

## References
- https://git.kernel.org/stable/c/102b82708c1523b36d421cb8687746906069bc17
- https://git.kernel.org/stable/c/a46bebd502fe1a3bd1d22f64cedd93e7e7702693
- https://git.kernel.org/stable/c/b7724360714642099cec907f54f42e55f5325453
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53838.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53838
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
