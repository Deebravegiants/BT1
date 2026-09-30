# [M] CVE-2021-46906

## Summary
Severity: Medium
Advisory: CVE-2021-46906
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-02-26
Source: https://osv.dev/vulnerability/CVE-2021-46906
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: usbhid: fix info leak in hid_submit_ctrl

In hid_submit_ctrl(), the way of calculating the report length doesn't
take into account that report->size can be zero. When running the
syzkaller reproducer, a report of size 0 causes hid_submit_ctrl) to
calculate transfer_buffer_length as 16384. When this urb is passed to
the usb core layer, KMSAN reports an info leak of 16384 bytes.

To fix this, first modify hid_report_len() to account for the zero
report size case by using DIV_ROUND_UP for the division. Then, call it
from hid_submit_ctrl().

## References
- https://git.kernel.org/stable/c/41b1e71a2c57366b08dcca1a28b0d45ca69429ce
- https://git.kernel.org/stable/c/6be388f4a35d2ce5ef7dbf635a8964a5da7f799f
- https://git.kernel.org/stable/c/7f5a4b24cdbd7372770a02f23e347d7d9a9ac8f1
- https://git.kernel.org/stable/c/8c064eece9a51856f3f275104520c7e3017fc5c0
- https://git.kernel.org/stable/c/b1e3596416d74ce95cc0b7b38472329a3818f8a9
- https://git.kernel.org/stable/c/c5d3c142f2d57d40c55e65d5622d319125a45366
- https://git.kernel.org/stable/c/0e280502be1b003c3483ae03fc60dea554fcfa82
- https://git.kernel.org/stable/c/21883bff0fd854e07429a773ff18f1e9658f50e8
