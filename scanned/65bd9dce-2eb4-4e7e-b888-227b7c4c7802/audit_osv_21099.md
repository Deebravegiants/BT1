# [M] CVE-2021-40569

## Summary
Severity: Medium
Advisory: CVE-2021-40569
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-13
Source: https://osv.dev/vulnerability/CVE-2021-40569
Type: osv

## Details
The binary MP4Box in Gpac through 1.0.1 has a double-free vulnerability in the iloc_entry_del funciton in box_code_meta.c, which allows attackers to cause a denial of service.

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/issues/1890
- https://github.com/gpac/gpac/commit/b03c9f252526bb42fbd1b87b9f5e339c3cf2390a
