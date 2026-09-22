# [H] HID: multitouch: Correct devm device reference for hidinput input_dev name

## Summary
Severity: High
Advisory: CVE-2023-53454
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53454
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <4.14.326, >=4.15.0 <4.19.295, >=4.20.0 <5.4.257, >=5.5.0 <5.10.195, >=5.11.0 <5.15.132, >=5.16.0 <6.1.53, >=6.2.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: multitouch: Correct devm device reference for hidinput input_dev name

Reference the HID device rather than the input device for the devm
allocation of the input_dev name. Referencing the input_dev would lead to a
use-after-free when the input_dev was unregistered and subsequently fires a
uevent that depends on the name. At the point of firing the uevent, the
name would be freed by devres management.

Use devm_kasprintf to simplify the logic for allocating memory and
formatting the input_dev name string.

## References
- https://git.kernel.org/stable/c/15ec7cb55e7d88755aa01d44a7a1015a42bfce86
- https://git.kernel.org/stable/c/1d7833db9fd118415dace2ca157bfa603dec9c8c
- https://git.kernel.org/stable/c/2763732ec1e68910719c75b6b896e11b6d3d622b
- https://git.kernel.org/stable/c/39c70c19456e50dcb3abfe53539220dff0490f1d
- https://git.kernel.org/stable/c/4794394635293a3e74591351fff469cea7ad15a2
- https://git.kernel.org/stable/c/ac0d389402a6ff9ad92cea02c2d8c711483b91ab
- https://git.kernel.org/stable/c/b70ac7849248ec8128fa12f86e3655ba38838f29
- https://git.kernel.org/stable/c/dde88ab4e45beb60b217026207aa9c14c88d71ab
- https://git.kernel.org/stable/c/df7ca43fe090e1a56c216c8ebc106ef5fd49afc6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53454.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53454
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
