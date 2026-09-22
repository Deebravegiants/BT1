# [M] CVE-2022-34675

## Summary
Severity: Medium
Advisory: CVE-2022-34675
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-30
Source: https://osv.dev/vulnerability/CVE-2022-34675
Type: osv

## Details
NVIDIA Display Driver for Linux contains a vulnerability in the Virtual GPU Manager, where it does not check the return value from a null-pointer dereference, which may lead to denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00010.html
- https://nvidia.custhelp.com/app/answers/detail/a_id/5415
