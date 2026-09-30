# [H] CVE-2021-47485

## Summary
Severity: High
Advisory: CVE-2021-47485
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47485
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

IB/qib: Protect from buffer overflow in struct qib_user_sdma_pkt fields

Overflowing either addrlimit or bytes_togo can allow userspace to trigger
a buffer overflow of kernel memory. Check for overflows in all the places
doing math on user controlled buffers.

## References
- https://git.kernel.org/stable/c/0d4395477741608d123dad51def9fe50b7ebe952
- https://git.kernel.org/stable/c/0f8cdfff06829a0b0348b6debc29ff6a61967724
- https://git.kernel.org/stable/c/3f57c3f67fd93b4da86aeffea1ca32c484d054ad
- https://git.kernel.org/stable/c/60833707b968d5ae02a75edb7886dcd4a957cf0d
- https://git.kernel.org/stable/c/73d2892148aa4397a885b4f4afcfc5b27a325c42
- https://git.kernel.org/stable/c/bda41654b6e0c125a624ca35d6d20beb8015b5d0
- https://git.kernel.org/stable/c/c3e17e58f571f34c51aeb17274ed02c2ed5cf780
- https://git.kernel.org/stable/c/d39bf40e55e666b5905fdbd46a0dced030ce87be
