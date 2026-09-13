# [H] crypto: af_alg - Disallow concurrent writes in af_alg_sendmsg

## Summary
Severity: High
Advisory: CVE-2025-39964
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-13
Source: https://osv.dev/vulnerability/CVE-2025-39964
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <5.10.245, >=5.11.0 <5.15.194, >=5.16.0 <6.1.154, >=6.2.0 <6.6.108, >=6.7.0 <6.12.49, >=6.13.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: af_alg - Disallow concurrent writes in af_alg_sendmsg

Issuing two writes to the same af_alg socket is bogus as the
data will be interleaved in an unpredictable fashion.  Furthermore,
concurrent writes may create inconsistencies in the internal
socket state.

Disallow this by adding a new ctx->write field that indiciates
exclusive ownership for writing.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/0f28c4adbc4a97437874c9b669fd7958a8c6d6ce
- https://git.kernel.org/stable/c/1b34cbbf4f011a121ef7b2d7d6e6920a036d5285
- https://git.kernel.org/stable/c/1f323a48e9b5ebfe6dc7d130fdf5c3c0e92a07c8
- https://git.kernel.org/stable/c/45bcf60fe49b37daab1acee57b27211ad1574042
- https://git.kernel.org/stable/c/7c4491b5644e3a3708f3dbd7591be0a570135b84
- https://git.kernel.org/stable/c/9aee87da5572b3a14075f501752e209801160d3d
- https://git.kernel.org/stable/c/e4c1ec11132ec466f7362a95f36a506ce4dc08c9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39964.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39964
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
