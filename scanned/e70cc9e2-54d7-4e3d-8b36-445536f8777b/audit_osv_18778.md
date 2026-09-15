# [M] CVE-2020-36149

## Summary
Severity: Medium
Advisory: CVE-2020-36149
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-02-08
Source: https://osv.dev/vulnerability/CVE-2020-36149
Type: osv

## Details
Incorrect handling of input data in changeAttribute function in the libmysofa library 0.5 - 1.1 will lead to NULL pointer dereference and segmentation fault error in case of restrictive memory protection or near NULL pointer overwrite in case of no memory restrictions (e.g. in embedded environments).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RQLNZOVVONQSZZJHQVZT6NMOUUDMGBBR/
- https://github.com/hoene/libmysofa/issues/137
