# [H] serial: amba-pl011: synchronize DMA teardown

## Summary
Severity: High
Advisory: CVE-2026-80737
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-80737
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <5.10.267, >=5.11.0 <5.15.218, >=5.16.0 <6.1.185, >=6.2.0 <6.6.154, >=6.7.0 <6.12.106, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

serial: amba-pl011: synchronize DMA teardown

dmaengine_terminate_all() does not wait for a running callback, so the TX
callback can still touch the TX buffer after it is freed. The RX poll
timer reads the RX buffers without the port lock.

Switch to dmaengine_terminate_sync() and delete the RX timer before
freeing the buffers.

## References
- https://git.kernel.org/stable/c/440915499231e9db1c361aa45bb702e8fd3b4a32
- https://git.kernel.org/stable/c/44bd0ecc3444882d08ecfbc2b2418d2f463d3186
- https://git.kernel.org/stable/c/5974cb66681eac367107b05924744d7e3b49d41c
- https://git.kernel.org/stable/c/9f6989e477f03a4721d34bb4b09b17accd40283e
- https://git.kernel.org/stable/c/a38fae9d212e2d3ed5e9ec0ef773f8c0a27fb76e
- https://git.kernel.org/stable/c/c8c8e895f65fbf71ea6224e27cf8dab91b776e0d
- https://git.kernel.org/stable/c/f70c9d4fba46463a5b1c7b3ee9ee3b40c90dac03
- https://git.kernel.org/stable/c/fdfb46c387241b4eddd36d746793764413285913
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80737.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80737
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
