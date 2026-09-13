# [M] drm/xe: Fix possible exec queue leak in exec IOCTL

## Summary
Severity: Medium
Advisory: CVE-2024-53087
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53087
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: Fix possible exec queue leak in exec IOCTL

In a couple of places after an exec queue is looked up the exec IOCTL
returns on input errors without dropping the exec queue ref. Fix this
ensuring the exec queue ref is dropped on input error.

(cherry picked from commit 07064a200b40ac2195cb6b7b779897d9377e5e6f)

## References
- https://git.kernel.org/stable/c/2f92b77a8ce043fbda2664d9be4b66bdc57f67b7
- https://git.kernel.org/stable/c/af797b831d8975cb4610f396dcb7f03f4b9908e7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53087.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53087
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
