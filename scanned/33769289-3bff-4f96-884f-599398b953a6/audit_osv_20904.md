# [M] CVE-2021-38203

## Summary
Severity: Medium
Advisory: CVE-2021-38203
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-08
Source: https://osv.dev/vulnerability/CVE-2021-38203
Type: osv

## Details
btrfs in the Linux kernel before 5.13.4 allows attackers to cause a denial of service (deadlock) via processes that trigger allocation of new system chunks during times when there is a shortage of free space in the system space_info.

## References
- https://security.netapp.com/advisory/ntap-20210902-0010/
- https://github.com/torvalds/linux/commit/1cb3db1cf383a3c7dbda1aa0ce748b0958759947
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.4
