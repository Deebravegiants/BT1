# [C] crypto: safexcel - Add error handling for dma_map_sg() calls

## Summary
Severity: Critical
Advisory: CVE-2023-52687
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2023-52687
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.75, >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: safexcel - Add error handling for dma_map_sg() calls

Macro dma_map_sg() may return 0 on error. This patch enables
checks in case of the macro failure and ensures unmapping of
previously mapped buffers with dma_unmap_sg().

Found by Linux Verification Center (linuxtesting.org) with static
analysis tool SVACE.

## References
- https://git.kernel.org/stable/c/4c0ac81a172a69a7733290915276672787e904ec
- https://git.kernel.org/stable/c/8084b788c2fb1260f7d44c032d5124680b20d2b2
- https://git.kernel.org/stable/c/87e02063d07708cac5bfe9fd3a6a242898758ac8
- https://git.kernel.org/stable/c/fc0b785802b856566df3ac943e38a072557001c4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52687.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52687
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
