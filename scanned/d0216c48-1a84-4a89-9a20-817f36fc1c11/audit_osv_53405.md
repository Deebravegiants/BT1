# [H] CVE-2022-42261

## Summary
Severity: High
Advisory: CVE-2022-42261
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-30
Source: https://osv.dev/vulnerability/CVE-2022-42261
Type: osv

## Details
NVIDIA vGPU software contains a vulnerability in the Virtual GPU Manager (vGPU plugin), where an input index is not validated, which may lead to buffer overrun, which in turn may cause data tampering, information disclosure, or denial of service.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5415
- https://security.gentoo.org/glsa/202310-02
