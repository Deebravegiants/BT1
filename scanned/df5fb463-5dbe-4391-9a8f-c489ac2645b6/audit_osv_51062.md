# [M] CVE-2021-1095

## Summary
Severity: Medium
Advisory: CVE-2021-1095
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-22
Source: https://osv.dev/vulnerability/CVE-2021-1095
Type: osv

## Details
NVIDIA GPU Display Driver for Windows and Linux contains a vulnerability in the kernel mode layer (nvlddmkm.sys) handlers for all control calls with embedded parameters where dereferencing an untrusted pointer may lead to denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2022/01/msg00013.html
- https://security.gentoo.org/glsa/202310-02
- https://nvidia.custhelp.com/app/answers/detail/a_id/5211
