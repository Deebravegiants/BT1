# [M] CVE-2022-34679

## Summary
Severity: Medium
Advisory: CVE-2022-34679
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-30
Source: https://osv.dev/vulnerability/CVE-2022-34679
Type: osv

## Details
NVIDIA GPU Display Driver for Linux contains a vulnerability in the kernel mode layer handler, where an unhandled return value can lead to a null-pointer dereference, which may lead to denial of service.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5415
- https://security.gentoo.org/glsa/202310-02
