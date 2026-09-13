# [M] CVE-2018-20348

## Summary
Severity: Medium
Advisory: CVE-2018-20348
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-22
Source: https://osv.dev/vulnerability/CVE-2018-20348
Type: osv

## Details
libpff_item_tree_create_node in libpff_item_tree.c in libpff before experimental-20180714 allows attackers to cause a denial of service (infinite recursion) via a crafted file, related to libfdata_tree_get_node_value in libfdata_tree.c.

## References
- https://github.com/libyal/libpff/issues/48
