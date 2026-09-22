# [M] CVE-2021-33364

## Summary
Severity: Medium
Advisory: CVE-2021-33364
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-09-13
Source: https://osv.dev/vulnerability/CVE-2021-33364
Type: osv

## Details
Memory leak in the def_parent_box_new function in MP4Box in GPAC 1.0.1 allows attackers to read memory via a crafted file.

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/commit/fe5155cf047252d1c4cb91602048bfa682af0ea7
- https://github.com/gpac/gpac/issues/1783
