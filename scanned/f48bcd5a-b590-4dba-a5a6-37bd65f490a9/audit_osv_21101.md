# [H] CVE-2021-40571

## Summary
Severity: High
Advisory: CVE-2021-40571
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-01-13
Source: https://osv.dev/vulnerability/CVE-2021-40571
Type: osv

## Details
The binary MP4Box in Gpac 1.0.1 has a double-free vulnerability in the ilst_box_read function in box_code_apple.c, which allows attackers to cause a denial of service, even code execution and escalation of privileges.

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/issues/1895
- https://github.com/gpac/gpac/commit/a69b567b8c95c72f9560c873c5ab348be058f340
