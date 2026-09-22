# [H] listmount: don't call path_put() under namespace semaphore

## Summary
Severity: High
Advisory: CVE-2025-40203
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40203
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.54, >=6.13.0 <6.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

listmount: don't call path_put() under namespace semaphore

Massage listmount() and make sure we don't call path_put() under the
namespace semaphore. If we put the last reference we're fscked.

## References
- https://git.kernel.org/stable/c/659874b7ee4976ad9ce476e07fd36bc67b3537f1
- https://git.kernel.org/stable/c/9c80da26fda2fdcaac7f92b5908875b3108830ff
- https://git.kernel.org/stable/c/c1f86d0ac322c7e77f6f8dbd216c65d39358ffc0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40203.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40203
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
