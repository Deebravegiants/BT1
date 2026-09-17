# [H] CVE-2021-47670

## Summary
Severity: High
Advisory: CVE-2021-47670
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-17
Source: https://osv.dev/vulnerability/CVE-2021-47670
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: peak_usb: fix use after free bugs

After calling peak_usb_netif_rx_ni(skb), dereferencing skb is unsafe.
Especially, the can_frame cf which aliases skb memory is accessed
after the peak_usb_netif_rx_ni().

Reordering the lines solves the issue.

## References
- https://git.kernel.org/stable/c/50aca891d7a554db0901b245167cd653d73aaa71
- https://git.kernel.org/stable/c/5408824636fa0dfedb9ecb0d94abd573131bfbbe
- https://git.kernel.org/stable/c/ddd1416f44130377798c1430b76503513b7497c2
- https://git.kernel.org/stable/c/ec939c13c3fff2114479769c8380b7f1a54feca9
