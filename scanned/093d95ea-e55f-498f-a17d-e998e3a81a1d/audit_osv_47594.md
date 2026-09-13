# [M] CVE-2016-8826

## Summary
Severity: Medium
Advisory: CVE-2016-8826
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-16
Source: https://osv.dev/vulnerability/CVE-2016-8826
Type: osv

## Details
All versions of NVIDIA GPU Display Driver contain a vulnerability in the kernel mode layer (nvlddmkm.sys for Windows or nvidia.ko for Linux) where a user can cause a GPU interrupt storm, leading to a denial of service.

## References
- http://nvidia.custhelp.com/app/answers/detail/a_id/4278
- http://www.securityfocus.com/bid/94957
- http://nvidia.custhelp.com/app/answers/detail/a_id/4278
