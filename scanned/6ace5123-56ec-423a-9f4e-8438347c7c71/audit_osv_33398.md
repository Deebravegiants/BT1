# [H] drm/panthor: Flush shmem writes before mapping buffers CPU-uncached

## Summary
Severity: High
Advisory: CVE-2025-40276
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-12-06
Source: https://osv.dev/vulnerability/CVE-2025-40276
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.64, >=6.13.0 <6.17.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panthor: Flush shmem writes before mapping buffers CPU-uncached

The shmem layer zeroes out the new pages using cached mappings, and if
we don't CPU-flush we might leave dirty cachelines behind, leading to
potential data leaks and/or asynchronous buffer corruption when dirty
cachelines are evicted.

## References
- https://git.kernel.org/stable/c/576c930e5e7dcb937648490611a83f1bf0171048
- https://git.kernel.org/stable/c/7a12f9c96d06b145562f76ffb20369b4692f0911
- https://git.kernel.org/stable/c/8355eea2a2e9c323021dfdcb95d7767d382123c4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40276.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40276
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
