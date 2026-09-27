# [M] CVE-2022-28192

## Summary
Severity: Medium
Advisory: CVE-2022-28192
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-05-17
Source: https://osv.dev/vulnerability/CVE-2022-28192
Type: osv

## Details
NVIDIA vGPU software contains a vulnerability in the Virtual GPU Manager (nvidia.ko), where it may lead to a use-after-free, which in turn may cause denial of service. This attack is complex to carry out because the attacker needs to have control over freeing some host side resources out of sequence, which requires elevated privileges.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5353
