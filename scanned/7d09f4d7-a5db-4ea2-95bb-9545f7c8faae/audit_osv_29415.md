# [H] udf: Avoid using corrupted block bitmap buffer

## Summary
Severity: High
Advisory: CVE-2024-42306
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42306
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.3.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

udf: Avoid using corrupted block bitmap buffer

When the filesystem block bitmap is corrupted, we detect the corruption
while loading the bitmap and fail the allocation with error. However the
next allocation from the same bitmap will notice the bitmap buffer is
already loaded and tries to allocate from the bitmap with mixed results
(depending on the exact nature of the bitmap corruption). Fix the
problem by using BH_verified bit to indicate whether the bitmap is valid
or not.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/2199e157a465aaf98294d3932797ecd7fce942d5
- https://git.kernel.org/stable/c/271cab2ca00652bc984e269cf1208699a1e09cdd
- https://git.kernel.org/stable/c/57053b3bcf3403b80db6f65aba284d7dfe7326af
- https://git.kernel.org/stable/c/6a43e3c210df6c5f00570f4be49a897677dbcb64
- https://git.kernel.org/stable/c/8ca170c39eca7cad6e0cfeb24e351d8f8eddcd65
- https://git.kernel.org/stable/c/a90d4471146de21745980cba51ce88e7926bcc4f
- https://git.kernel.org/stable/c/cae9e59cc41683408b70b9ab569f8654866ba914
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42306.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42306
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
