# [M] CVE-2021-47374

## Summary
Severity: Medium
Advisory: CVE-2021-47374
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47374
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

dma-debug: prevent an error message from causing runtime problems

For some drivers, that use the DMA API. This error message can be reached
several millions of times per second, causing spam to the kernel's printk
buffer and bringing the CPU usage up to 100% (so, it should be rate
limited). However, since there is at least one driver that is in the
mainline and suffers from the error condition, it is more useful to
err_printk() here instead of just rate limiting the error message (in hopes
that it will make it easier for other drivers that suffer from this issue
to be spotted).

## References
- https://git.kernel.org/stable/c/510e1a724ab1bf38150be2c1acabb303f98d0047
- https://git.kernel.org/stable/c/de4afec2d2946c92c62a15ab341c70b287289e6a
