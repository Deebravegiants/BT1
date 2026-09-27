# [H] CVE-2017-6272

## Summary
Severity: High
Advisory: CVE-2017-6272
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-22
Source: https://osv.dev/vulnerability/CVE-2017-6272
Type: osv

## Details
NVIDIA GPU Display Driver contains a vulnerability in the kernel mode layer handler where a value passed from a user to the driver is not correctly validated and used as the index to an array which may lead to a denial of service or possible escalation of privileges.

## References
- http://nvidia.custhelp.com/app/answers/detail/a_id/4544
- http://www.securityfocus.com/bid/100997
