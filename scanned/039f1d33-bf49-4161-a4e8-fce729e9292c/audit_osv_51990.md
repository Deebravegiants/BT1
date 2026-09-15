# [M] CVE-2021-46932

## Summary
Severity: Medium
Advisory: CVE-2021-46932
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46932
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

Input: appletouch - initialize work before device registration

Syzbot has reported warning in __flush_work(). This warning is caused by
work->func == NULL, which means missing work initialization.

This may happen, since input_dev->close() calls
cancel_work_sync(&dev->work), but dev->work initalization happens _after_
input_register_device() call.

So this patch moves dev->work initialization before registering input
device

## References
- https://git.kernel.org/stable/c/d2cb2bf39a6d17ef4bdc0e59c1a35cf5751ad8f4
- https://git.kernel.org/stable/c/e79ff8c68acb1eddf709d3ac84716868f2a91012
- https://git.kernel.org/stable/c/292d2ac61fb0d9276a0f7b7ce4f50426f2a1c99f
- https://git.kernel.org/stable/c/975774ea7528b489930b76a77ffc4d5379b95ff2
- https://git.kernel.org/stable/c/9f329d0d6c91142cf0ad08d23c72dd195db2633c
- https://git.kernel.org/stable/c/9f3ccdc3f6ef10084ceb3a47df0961bec6196fd0
- https://git.kernel.org/stable/c/a02e1404e27855089d2b0a0acc4652c2ce65fe46
- https://git.kernel.org/stable/c/d1962f263a176f493400b8f91bfbf2bfedce951e
