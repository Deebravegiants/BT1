# [M] CVE-2019-19047

## Summary
Severity: Medium
Advisory: CVE-2019-19047
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19047
Type: osv

## Details
A memory leak in the mlx5_fw_fatal_reporter_dump() function in drivers/net/ethernet/mellanox/mlx5/core/health.c in the Linux kernel before 5.3.11 allows attackers to cause a denial of service (memory consumption) by triggering mlx5_crdump_collect() failures, aka CID-c7ed6d0183d5.

## References
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4225-1/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.11
- https://github.com/torvalds/linux/commit/c7ed6d0183d5ea9bc31bcaeeba4070bd62546471
