# [M] CVE-2021-32269

## Summary
Severity: Medium
Advisory: CVE-2021-32269
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-32269
Type: osv

## Details
An issue was discovered in gpac through 20200801. A NULL pointer dereference exists in the function ilst_item_box_dump located in box_dump.c. It allows an attacker to cause Denial of Service.

## References
- https://github.com/gpac/gpac/issues/1574
