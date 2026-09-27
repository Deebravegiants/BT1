# [H] CVE-2021-1052

## Summary
Severity: High
Advisory: CVE-2021-1052
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-08
Source: https://osv.dev/vulnerability/CVE-2021-1052
Type: osv

## Details
NVIDIA GPU Display Driver for Windows and Linux, all versions, contains a vulnerability in the kernel mode layer (nvlddmkm.sys) handler for DxgkDdiEscape or IOCTL in which user-mode clients can access legacy privileged APIs, which may lead to denial of service, escalation of privileges, and information disclosure.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5142
- https://security.gentoo.org/glsa/202310-02
