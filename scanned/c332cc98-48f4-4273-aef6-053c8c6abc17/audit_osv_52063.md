# [M] CVE-2021-47024

## Summary
Severity: Medium
Advisory: CVE-2021-47024
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47024
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

vsock/virtio: free queued packets when closing socket

As reported by syzbot [1], there is a memory leak while closing the
socket. We partially solved this issue with commit ac03046ece2b
("vsock/virtio: free packets during the socket release"), but we
forgot to drain the RX queue when the socket is definitely closed by
the scheduled work.

To avoid future issues, let's use the new virtio_transport_remove_sock()
to drain the RX queue before removing the socket from the af_vsock lists
calling vsock_remove_sock().

[1] https://syzkaller.appspot.com/bug?extid=24452624fc4c571eedd9

## References
- https://git.kernel.org/stable/c/27691665145e74a45034a9dccf1150cf1894763a
- https://git.kernel.org/stable/c/37c38674ef2f8d7e8629e5d433c37d6c1273d16b
- https://git.kernel.org/stable/c/8432b8114957235f42e070a16118a7f750de9d39
- https://git.kernel.org/stable/c/b605673b523fe33abeafb2136759bcbc9c1e6ebf
