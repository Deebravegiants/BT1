# [H] crypto: starfive - Do not free stack buffer

## Summary
Severity: High
Advisory: CVE-2024-39478
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-05
Source: https://osv.dev/vulnerability/CVE-2024-39478
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.156, >=6.7.0 <6.9.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: starfive - Do not free stack buffer

RSA text data uses variable length buffer allocated in software stack.
Calling kfree on it causes undefined behaviour in subsequent operations.

## References
- https://git.kernel.org/stable/c/5944de192663f272033501dcd322b008fca72006
- https://git.kernel.org/stable/c/bfd861dadd3a45de257b3d328bf49b64a6f9c5f1
- https://git.kernel.org/stable/c/d7f01649f4eaf1878472d3d3f480ae1e50d98f6c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39478.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39478
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
