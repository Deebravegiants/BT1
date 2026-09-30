# [H] CVE-2021-47356

## Summary
Severity: High
Advisory: CVE-2021-47356
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47356
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mISDN: fix possible use-after-free in HFC_cleanup()

This module's remove path calls del_timer(). However, that function
does not wait until the timer handler finishes. This means that the
timer handler may still be running after the driver's remove function
has finished, which would result in a use-after-free.

Fix by calling del_timer_sync(), which makes sure the timer handler
has finished, and unable to re-schedule itself.

## References
- https://git.kernel.org/stable/c/7867ddc5f3de7f289aee63233afc0df4b62834c5
- https://git.kernel.org/stable/c/ed7c3739d0a07e2ec3ccbffe7e93cea01c438cda
- https://git.kernel.org/stable/c/009fc857c5f6fda81f2f7dd851b2d54193a8e733
- https://git.kernel.org/stable/c/3ecd228c636ee17c14662729737fa07242a93cb0
- https://git.kernel.org/stable/c/49331c07ef0f8fdfa42b30ba6a83a657b29d7fbe
- https://git.kernel.org/stable/c/54ff3202928952a100c477248e65ac6db01258a7
- https://git.kernel.org/stable/c/5f2818185da0fe82a932f0856633038b66faf124
- https://git.kernel.org/stable/c/b7ee9ae1e0cf55a037c4a99af2acc5d78cb7802d
- https://git.kernel.org/stable/c/61370ff07e0acc657559a8fac02551dfeb9d3020
