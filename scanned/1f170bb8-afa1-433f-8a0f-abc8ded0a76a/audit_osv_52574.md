# [H] CVE-2021-47596

## Summary
Severity: High
Advisory: CVE-2021-47596
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47596
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: hns3: fix use-after-free bug in hclgevf_send_mbx_msg

Currently, the hns3_remove function firstly uninstall client instance,
and then uninstall acceletion engine device. The netdevice is freed in
client instance uninstall process, but acceletion engine device uninstall
process still use it to trace runtime information. This causes a use after
free problem.

So fixes it by check the instance register state to avoid use after free.

## References
- https://git.kernel.org/stable/c/12512bc8f25b8ba9795dfbae0e9ca57ff13fd542
- https://git.kernel.org/stable/c/27cbf64a766e86f068ce6214f04c00ceb4db1af4
- https://git.kernel.org/stable/c/4f4a353f6fe033807cd026a5de81c67469ff19b0
