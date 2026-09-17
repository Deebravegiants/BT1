# [M] CVE-2019-19045

## Summary
Severity: Medium
Advisory: CVE-2019-19045
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19045
Type: osv

## Details
A memory leak in the mlx5_fpga_conn_create_cq() function in drivers/net/ethernet/mellanox/mlx5/core/fpga/conn.c in the Linux kernel before 5.3.11 allows attackers to cause a denial of service (memory consumption) by triggering mlx5_vector2eqn() failures, aka CID-c8c2a057fdc7.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.11
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4227-1/
- https://usn.ubuntu.com/4227-2/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://usn.ubuntu.com/4225-1/
- https://usn.ubuntu.com/4225-2/
- https://usn.ubuntu.com/4226-1/
- https://github.com/torvalds/linux/commit/c8c2a057fdc7de1cd16f4baa51425b932a42eb39
