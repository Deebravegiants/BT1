# [M] wifi: iwlwifi: fw: fix memory leak in debugfs

## Summary
Severity: Medium
Advisory: CVE-2023-53422
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53422
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.180, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: fw: fix memory leak in debugfs

Fix a memory leak that occurs when reading the fw_info
file all the way, since we return NULL indicating no
more data, but don't free the status tracking object.

## References
- https://git.kernel.org/stable/c/37f64bc8e001f216566d17ef9fd5608c762ebcd4
- https://git.kernel.org/stable/c/3d90d2f4a018fe8cfd65068bc6350b6222be4852
- https://git.kernel.org/stable/c/89496d6cff297c88fe0286a440c380ceb172da2b
- https://git.kernel.org/stable/c/b830ba20b43be52eae7d4087b61a0079dec56820
- https://git.kernel.org/stable/c/e302e9ca14a86a80eadfb24a34d8675aadaf3ef3
- https://git.kernel.org/stable/c/fe17124282da055cb2e53f0131521459b5c7866c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53422.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53422
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
