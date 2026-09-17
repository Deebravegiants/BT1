# [H] crypto: lzo - Fix compression buffer overrun

## Summary
Severity: High
Advisory: CVE-2025-38068
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-38068
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.23 <5.15.185, >=5.16.0 <6.1.141, >=6.2.0 <6.6.93, >=6.7.0 <6.12.31, >=6.13.0 <6.14.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: lzo - Fix compression buffer overrun

Unlike the decompression code, the compression code in LZO never
checked for output overruns.  It instead assumes that the caller
always provides enough buffer space, disregarding the buffer length
provided by the caller.

Add a safe compression interface that checks for the end of buffer
before each write.  Use the safe interface in crypto/lzo.

## References
- https://git.kernel.org/stable/c/0acdc4d6e679ba31d01e3e7e2e4124b76d6d8e2a
- https://git.kernel.org/stable/c/167373d77c70c2b558aae3e327b115249bb2652c
- https://git.kernel.org/stable/c/4b173bb2c4665c23f8fcf5241c7b06dfa6b5b111
- https://git.kernel.org/stable/c/7caad075acb634a74911830d6386c50ea12566cd
- https://git.kernel.org/stable/c/a98bd864e16f91c70b2469adf013d713d04d1d13
- https://git.kernel.org/stable/c/cc47f07234f72cbd8e2c973cdbf2a6730660a463
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38068.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38068
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
