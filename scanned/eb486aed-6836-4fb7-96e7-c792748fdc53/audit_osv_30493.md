# [H] NFSD: Never decrement pending_async_copies on error

## Summary
Severity: High
Advisory: CVE-2024-53073
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53073
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.3 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Never decrement pending_async_copies on error

The error flow in nfsd4_copy() calls cleanup_async_copy(), which
already decrements nn->pending_async_copies.

## References
- https://git.kernel.org/stable/c/1421883aa30c5d26bc3370e2d19cb350f0d5ca28
- https://git.kernel.org/stable/c/8286f8b622990194207df9ab852e0f87c60d35e9
- https://git.kernel.org/stable/c/9467c49437e948c541569007cd412d577942e635
- https://git.kernel.org/stable/c/949ee5d44d1fd95119b29b3382a933cdc617bf9e
- https://git.kernel.org/stable/c/ed98d26021db0fe62c327aa9f5e57a90bff3fa94
- https://git.kernel.org/stable/c/fb79d68a36e21960341ccab07d1ac06d93830321
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53073.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53073
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
