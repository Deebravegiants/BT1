# [M] CVE-2022-42895

## Summary
Severity: Medium
Advisory: CVE-2022-42895
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-11-23
Source: https://osv.dev/vulnerability/CVE-2022-42895
Type: osv

## Details
There is an infoleak vulnerability in the Linux kernel's net/bluetooth/l2cap_core.c's l2cap_parse_conf_req function which can be used to leak kernel pointers remotely.
We recommend upgrading past commit  https://github.com/torvalds/linux/commit/b1a2cd50c0357f243b7435a732b4e62ba3157a2e https://www.google.com/url

## References
- https://github.com/torvalds/linux/commit/b1a2cd50c0357f243b7435a732b4e62ba3157a2e
- https://kernel.dance/#b1a2cd50c0357f243b7435a732b4e62ba3157a2e
- https://github.com/torvalds/linux/commit/b1a2cd50c0357f243b7435a732b4e62ba3157a2e
- https://kernel.dance/#b1a2cd50c0357f243b7435a732b4e62ba3157a2e
