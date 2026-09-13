# [M] CVE-2021-47231

## Summary
Severity: Medium
Advisory: CVE-2021-47231
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47231
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: mcba_usb: fix memory leak in mcba_usb

Syzbot reported memory leak in SocketCAN driver for Microchip CAN BUS
Analyzer Tool. The problem was in unfreed usb_coherent.

In mcba_usb_start() 20 coherent buffers are allocated and there is
nothing, that frees them:

1) In callback function the urb is resubmitted and that's all
2) In disconnect function urbs are simply killed, but URB_FREE_BUFFER
   is not set (see mcba_usb_start) and this flag cannot be used with
   coherent buffers.

Fail log:
| [ 1354.053291][ T8413] mcba_usb 1-1:0.0 can0: device disconnected
| [ 1367.059384][ T8420] kmemleak: 20 new suspected memory leaks (see /sys/kernel/debug/kmem)

So, all allocated buffers should be freed with usb_free_coherent()
explicitly

NOTE:
The same pattern for allocating and freeing coherent buffers
is used in drivers/net/can/usb/kvaser_usb/kvaser_usb_core.c

## References
- https://git.kernel.org/stable/c/d0760a4ef85697bc756d06eae17ae27f3f055401
- https://git.kernel.org/stable/c/6bd3d80d1f019cefa7011056c54b323f1d8b8e83
- https://git.kernel.org/stable/c/6f87c0e21ad20dd3d22108e33db1c552dfa352a0
- https://git.kernel.org/stable/c/89df95ce32be204eef2e7d4b2f6fb552fb191a68
- https://git.kernel.org/stable/c/91c02557174be7f72e46ed7311e3bea1939840b0
- https://git.kernel.org/stable/c/a115198caaab6d663bef75823a3c5f0802306d60
