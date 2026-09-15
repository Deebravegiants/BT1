# [C] CVE-2022-28181

## Summary
Severity: Critical
Advisory: CVE-2022-28181
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-05-17
Source: https://osv.dev/vulnerability/CVE-2022-28181
Type: osv

## Details
NVIDIA GPU Display Driver for Windows and Linux contains a vulnerability in the kernel mode layer, where an unprivileged regular user on the network can cause an out-of-bounds write through a specially crafted shader, which may lead to code execution, denial of service, escalation of privileges, information disclosure, and data tampering. The scope of the impact may extend to other components.

## References
- https://security.gentoo.org/glsa/202310-02
- https://nvidia.custhelp.com/app/answers/detail/a_id/5353
