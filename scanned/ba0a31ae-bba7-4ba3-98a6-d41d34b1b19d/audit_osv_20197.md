# [M] CVE-2021-32132

## Summary
Severity: Medium
Advisory: CVE-2021-32132
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-13
Source: https://osv.dev/vulnerability/CVE-2021-32132
Type: osv

## Details
The abst_box_size function in GPAC 1.0.1 allows attackers to cause a denial of service (NULL pointer dereference) via a crafted file in the MP4Box command.

## References
- https://github.com/gpac/gpac/commit/e74be5976a6fee059c638050a237893f7e9a3b23
- https://github.com/gpac/gpac/issues/1753
