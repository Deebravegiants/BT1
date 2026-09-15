# [H] net/mlx5: Collect command failures data only for known commands

## Summary
Severity: High
Advisory: CVE-2023-53340
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53340
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.31, >=6.2.0 <6.3.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: Collect command failures data only for known commands

DEVX can issue a general command, which is not used by mlx5 driver.
In case such command is failed, mlx5 is trying to collect the failure
data, However, mlx5 doesn't create a storage for this command, since
mlx5 doesn't use it. This lead to array-index-out-of-bounds error.

Fix it by checking whether the command is known before collecting the
failure data.

## References
- https://git.kernel.org/stable/c/2a0a935fb64ee8af253b9c6133bb6702fb152ac2
- https://git.kernel.org/stable/c/411e4d6caa7f7169192b8dacc8421ac4fd64a354
- https://git.kernel.org/stable/c/d8b6f175235d7327b4e1b13216859e89496dfbd5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53340.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53340
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
