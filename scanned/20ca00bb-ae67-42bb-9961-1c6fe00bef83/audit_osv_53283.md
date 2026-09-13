# [H] CVE-2022-3625

## Summary
Severity: High
Advisory: CVE-2022-3625
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-21
Source: https://osv.dev/vulnerability/CVE-2022-3625
Type: osv

## Details
A vulnerability was found in Linux Kernel. It has been classified as critical. This affects the function devlink_param_set/devlink_param_get of the file net/core/devlink.c of the component IPsec. The manipulation leads to use after free. It is recommended to apply a patch to fix this issue. The identifier VDB-211929 was assigned to this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://vuldb.com/?id.211929
- https://git.kernel.org/pub/scm/linux/kernel/git/klassert/ipsec-next.git/commit/?id=6b4db2e528f650c7fb712961aac36455468d5902
