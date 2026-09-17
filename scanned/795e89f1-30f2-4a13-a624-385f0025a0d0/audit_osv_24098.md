# [H] dmaengine: sf-pdma: Add multithread support for a DMA channel

## Summary
Severity: High
Advisory: CVE-2022-50145
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50145
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.137, >=5.11.0 <5.15.61, >=5.16.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: sf-pdma: Add multithread support for a DMA channel

When we get a DMA channel and try to use it in multiple threads it
will cause oops and hanging the system.

% echo 64 > /sys/module/dmatest/parameters/threads_per_chan
% echo 10000 > /sys/module/dmatest/parameters/iterations
% echo 1 > /sys/module/dmatest/parameters/run
[   89.480664] Unable to handle kernel NULL pointer dereference at virtual
               address 00000000000000a0
[   89.488725] Oops [#1]
[   89.494708] CPU: 2 PID: 1008 Comm: dma0chan0-copy0 Not tainted
               5.17.0-rc5
[   89.509385] epc : vchan_find_desc+0x32/0x46
[   89.513553]  ra : sf_pdma_tx_status+0xca/0xd6

This happens because of data race. Each thread rewrite channels's
descriptor as soon as device_prep_dma_memcpy() is called. It leads to the
situation when the driver thinks that it uses right descriptor that
actually is freed or substituted for other one.

With current fixes a descriptor changes its value only when it has
been used. A new descriptor is acquired from vc->desc_issued queue that
is already filled with descriptors that are ready to be sent. Threads
have no direct access to DMA channel descriptor. Now it is just possible
to queue a descriptor for further processing.

## References
- https://git.kernel.org/stable/c/4c7350b1dd8a192af844de32fc99b9e34c876fda
- https://git.kernel.org/stable/c/5ab2782c944e324008ef5d658f2494a9f0e3c5ac
- https://git.kernel.org/stable/c/a93b3f1e11971a91b6441b6d47488f4492cc113f
- https://git.kernel.org/stable/c/b2cc5c465c2cb8ab697c3fd6583c614e3f6cfbcc
- https://git.kernel.org/stable/c/b9b4992f897be9b0b9e3a3b956cab6b75ccc3f11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50145.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50145
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
