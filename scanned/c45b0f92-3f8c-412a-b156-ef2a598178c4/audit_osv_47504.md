# [H] CVE-2016-7382

## Summary
Severity: High
Advisory: CVE-2016-7382
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-11-08
Source: https://osv.dev/vulnerability/CVE-2016-7382
Type: osv

## Details
For the NVIDIA Quadro, NVS, GeForce, and Tesla products, NVIDIA GPU Display Driver contains a vulnerability in the kernel mode layer (nvlddmkm.sys for Windows or nvidia.ko for Linux) handler where a missing permissions check may allow users to gain access to arbitrary physical memory, leading to an escalation of privileges.

## References
- https://support.lenovo.com/us/en/solutions/LEN-10822
- http://www.securityfocus.com/bid/94177
- http://nvidia.custhelp.com/app/answers/detail/a_id/4246
- http://nvidia.custhelp.com/app/answers/detail/a_id/4247
