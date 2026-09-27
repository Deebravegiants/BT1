# [M] dmaengine: fix NULL pointer in channel unregistration function

## Summary
Severity: Medium
Advisory: CVE-2023-52492
Ecosystem: Linux
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2023-52492
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.76, >=6.2.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: fix NULL pointer in channel unregistration function

__dma_async_device_channel_register() can fail. In case of failure,
chan->local is freed (with free_percpu()), and chan->local is nullified.
When dma_async_device_unregister() is called (because of managed API or
intentionally by DMA controller driver), channels are unconditionally
unregistered, leading to this NULL pointer:
[    1.318693] Unable to handle kernel NULL pointer dereference at virtual address 00000000000000d0
[...]
[    1.484499] Call trace:
[    1.486930]  device_del+0x40/0x394
[    1.490314]  device_unregister+0x20/0x7c
[    1.494220]  __dma_async_device_channel_unregister+0x68/0xc0

Look at dma_async_device_register() function error path, channel device
unregistration is done only if chan->local is not NULL.

Then add the same condition at the beginning of
__dma_async_device_channel_unregister() function, to avoid NULL pointer
issue whatever the API used to reach this function.

## References
- https://git.kernel.org/stable/c/047fce470412ab64cb7345f9ff5d06919078ad79
- https://git.kernel.org/stable/c/2ab32986a0b9e329eb7f8f04dd57cc127f797c08
- https://git.kernel.org/stable/c/7f0ccfad2031eddcc510caf4e57f2d4aa2d8a50b
- https://git.kernel.org/stable/c/9263fd2a63487c6d04cbb7b74a48fb12e1e352d0
- https://git.kernel.org/stable/c/9de69732dde4e443c1c7f89acbbed2c45a6a8e17
- https://git.kernel.org/stable/c/f5c24d94512f1b288262beda4d3dcb9629222fc7
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52492.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52492
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
