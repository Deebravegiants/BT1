# [M] accel/habanalabs: postpone mem_mgr IDR destruction to hpriv_release()

## Summary
Severity: Medium
Advisory: CVE-2023-53353
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53353
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/habanalabs: postpone mem_mgr IDR destruction to hpriv_release()

The memory manager IDR is currently destroyed when user releases the
file descriptor.
However, at this point the user context might be still held, and memory
buffers might be still in use.
Later on, calls to release those buffers will fail due to not finding
their handles in the IDR, leading to a memory leak.
To avoid this leak, split the IDR destruction from the memory manager
fini, and postpone it to hpriv_release() when there is no user context
and no buffers are used.

## References
- https://git.kernel.org/stable/c/2e8e9a895c4589f124a37fc84d123b5114406e94
- https://git.kernel.org/stable/c/840de329ca99cafd0cdde9c6ac160b1330942aba
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53353.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53353
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
