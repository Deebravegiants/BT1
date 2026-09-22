# [H] CVE-2023-0185

## Summary
Severity: High
Advisory: CVE-2023-0185
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-04-01
Source: https://osv.dev/vulnerability/CVE-2023-0185
Type: osv

## Details
NVIDIA GPU Display Driver for Linux contains a vulnerability in the kernel mode layer, where sign conversion issuescasting an unsigned primitive to signed may lead to denial of service or information disclosure.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5452
- https://security.gentoo.org/glsa/202310-02
