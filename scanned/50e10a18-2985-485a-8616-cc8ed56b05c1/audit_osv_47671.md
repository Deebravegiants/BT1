# [H] CVE-2017-0350

## Summary
Severity: High
Advisory: CVE-2017-0350
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-09
Source: https://osv.dev/vulnerability/CVE-2017-0350
Type: osv

## Details
All versions of the NVIDIA GPU Display Driver contain a vulnerability in the kernel mode layer handler where a value passed from a user to the driver is not correctly validated and used in an offset calculation may lead to denial of service or potential escalation of privileges.

## References
- http://nvidia.custhelp.com/app/answers/detail/a_id/4462
- http://www.securityfocus.com/bid/98490
