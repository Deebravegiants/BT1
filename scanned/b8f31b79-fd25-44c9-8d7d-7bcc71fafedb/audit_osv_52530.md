# [C] CVE-2021-47548

## Summary
Severity: Critical
Advisory: CVE-2021-47548
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47548
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ethernet: hisilicon: hns: hns_dsaf_misc: fix a possible array overflow in hns_dsaf_ge_srst_by_port()

The if statement:
  if (port >= DSAF_GE_NUM)
        return;

limits the value of port less than DSAF_GE_NUM (i.e., 8).
However, if the value of port is 6 or 7, an array overflow could occur:
  port_rst_off = dsaf_dev->mac_cb[port]->port_rst_off;

because the length of dsaf_dev->mac_cb is DSAF_MAX_PORT_NUM (i.e., 6).

To fix this possible array overflow, we first check port and if it is
greater than or equal to DSAF_MAX_PORT_NUM, the function returns.

## References
- https://git.kernel.org/stable/c/fc7ffa7f10b9454a86369405d9814bf141b30627
- https://git.kernel.org/stable/c/22519eff7df2d88adcc2568d86046ce1e2b52803
- https://git.kernel.org/stable/c/948968f8747650447c8f21c9fdba0e1973be040b
- https://git.kernel.org/stable/c/99bb25cb6753beaf2c2bc37927c2ecc0ceff3f6d
- https://git.kernel.org/stable/c/a66998e0fbf213d47d02813b9679426129d0d114
- https://git.kernel.org/stable/c/abbd5faa0748d0aa95d5191d56ff7a17a6275bd1
- https://git.kernel.org/stable/c/dd07f8971b81ad98cc754b179b331b57f35aa1ff
