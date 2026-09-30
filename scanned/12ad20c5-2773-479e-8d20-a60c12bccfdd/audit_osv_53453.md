# [H] CVE-2022-42896

## Summary
Severity: High
Advisory: CVE-2022-42896
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-23
Source: https://osv.dev/vulnerability/CVE-2022-42896
Type: osv

## Details
There are use-after-free vulnerabilities in the Linux kernel's net/bluetooth/l2cap_core.c's l2cap_connect and l2cap_le_connect_req functions which may allow code execution and leaking kernel memory (respectively) remotely via Bluetooth. A remote attacker could execute code leaking kernel memory via Bluetooth if within proximity of the victim.

We recommend upgrading past commit   https://www.google.com/url  https://github.com/torvalds/linux/commit/711f8c3fb3db61897080468586b970c87c61d9e4 https://www.google.com/url

## References
- https://github.com/torvalds/linux/commit/711f8c3fb3db61897080468586b970c87c61d9e4
- https://kernel.dance/#711f8c3fb3db61897080468586b970c87c61d9e4
