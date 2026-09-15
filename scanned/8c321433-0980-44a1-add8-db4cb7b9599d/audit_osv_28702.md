# [C] dma-direct: Leak pages on dma_set_decrypted() failure

## Summary
Severity: Critical
Advisory: CVE-2024-35939
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35939
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <6.1.86, >=6.2.0 <6.6.27, >=6.7.0 <6.8.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

dma-direct: Leak pages on dma_set_decrypted() failure

On TDX it is possible for the untrusted host to cause
set_memory_encrypted() or set_memory_decrypted() to fail such that an
error is returned and the resulting memory is shared. Callers need to
take care to handle these errors to avoid returning decrypted (shared)
memory to the page allocator, which could lead to functional or security
issues.

DMA could free decrypted/shared pages if dma_set_decrypted() fails. This
should be a rare case. Just leak the pages in this case instead of
freeing them.

## References
- https://git.kernel.org/stable/c/4031b72ca747a1e6e9ae4fa729e765b43363d66a
- https://git.kernel.org/stable/c/4e0cfb25d49da2e6261ad582f58ffa5b5dd8c8e9
- https://git.kernel.org/stable/c/b57326c96b7bc7638aa8c44e12afa2defe0c934c
- https://git.kernel.org/stable/c/b9fa16949d18e06bdf728a560f5c8af56d2bdcaf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35939.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35939
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
