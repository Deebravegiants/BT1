# [H] CVE-2022-42264

## Summary
Severity: High
Advisory: CVE-2022-42264
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-30
Source: https://osv.dev/vulnerability/CVE-2022-42264
Type: osv

## Details
NVIDIA GPU Display Driver for Linux contains a vulnerability in the kernel mode layer, where an unprivileged regular user can cause the use of an out-of-range pointer offset, which may lead to data tampering, data loss, information disclosure, or denial of service.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5415
- https://security.gentoo.org/glsa/202310-02
