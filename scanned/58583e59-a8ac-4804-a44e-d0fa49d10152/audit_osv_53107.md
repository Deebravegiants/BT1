# [H] CVE-2022-29156

## Summary
Severity: High
Advisory: CVE-2022-29156
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-13
Source: https://osv.dev/vulnerability/CVE-2022-29156
Type: osv

## Details
drivers/infiniband/ulp/rtrs/rtrs-clt.c in the Linux kernel before 5.16.12 has a double free related to rtrs_clt_dev_release.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.12
- https://security.netapp.com/advisory/ntap-20220602-0002/
- https://github.com/torvalds/linux/commit/8700af2cc18c919b2a83e74e0479038fd113c15d
