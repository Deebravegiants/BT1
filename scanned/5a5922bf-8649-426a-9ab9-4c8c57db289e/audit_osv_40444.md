# [H] net: mvpp2: sync RX data at the hardware packet offset

## Summary
Severity: High
Advisory: CVE-2026-53217
Ecosystem: Linux
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53217
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mvpp2: sync RX data at the hardware packet offset

mvpp2 programs the RX queue packet offset, so hardware writes received
data at dma_addr + MVPP2_SKB_HEADROOM. The current CPU sync starts at
dma_addr and only covers rx_bytes + MVPP2_MH_SIZE bytes, which syncs the
unused headroom and misses the same number of bytes at the packet tail.

On non-coherent DMA systems this can leave the CPU reading stale cache
contents for the end of the received frame.

Use dma_sync_single_range_for_cpu() with MVPP2_SKB_HEADROOM as the range
offset so the sync covers the Marvell header and packet data actually
written by hardware.

## References
- https://git.kernel.org/stable/c/180235600934bef6add3be637c296d6cf3272e67
- https://git.kernel.org/stable/c/19f8bc139e9b149d1e5bf75ae761d1bb8dd3e7d8
- https://git.kernel.org/stable/c/23548007b3c66d628fc7d6b80d1e23be04ea10d9
- https://git.kernel.org/stable/c/60412bdd1b2576659eac23a23d2d9ff96228a643
- https://git.kernel.org/stable/c/a13199fa224e9f776f4005d5037df03aa9ea8f37
- https://git.kernel.org/stable/c/a3ad9b5767c89531fc7dae951b51b0933dcf7051
- https://git.kernel.org/stable/c/bede0f481b9137d73d1cf64309cbe4b94818a5d6
- https://git.kernel.org/stable/c/e302206ad84a407a7e5f3f6fe767ff5efaace689
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53217.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53217
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
