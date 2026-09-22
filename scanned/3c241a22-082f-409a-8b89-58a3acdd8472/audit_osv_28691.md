# [H] nfsd: Fix error cleanup path in nfsd_rename()

## Summary
Severity: High
Advisory: CVE-2024-35914
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35914
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: Fix error cleanup path in nfsd_rename()

Commit a8b0026847b8 ("rename(): avoid a deadlock in the case of parents
having no common ancestor") added an error bail out path. However this
path does not drop the remount protection that has been acquired. Fix
the cleanup path to properly drop the remount protection.

## References
- https://git.kernel.org/stable/c/331e125e02c08ffaecc1074af78a988a278039bd
- https://git.kernel.org/stable/c/9fe6e9e7b58944037714442384075c17cfde1c56
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35914.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35914
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
