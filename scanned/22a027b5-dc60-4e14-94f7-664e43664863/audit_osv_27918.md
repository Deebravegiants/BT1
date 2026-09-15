# [H] crypto: arm64/neonbs - fix out-of-bounds access on short input

## Summary
Severity: High
Advisory: CVE-2024-26789
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/CVE-2024-26789
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.81, >=6.2.0 <6.6.21, >=6.7.0 <6.7.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: arm64/neonbs - fix out-of-bounds access on short input

The bit-sliced implementation of AES-CTR operates on blocks of 128
bytes, and will fall back to the plain NEON version for tail blocks or
inputs that are shorter than 128 bytes to begin with.

It will call straight into the plain NEON asm helper, which performs all
memory accesses in granules of 16 bytes (the size of a NEON register).
For this reason, the associated plain NEON glue code will copy inputs
shorter than 16 bytes into a temporary buffer, given that this is a rare
occurrence and it is not worth the effort to work around this in the asm
code.

The fallback from the bit-sliced NEON version fails to take this into
account, potentially resulting in out-of-bounds accesses. So clone the
same workaround, and use a temp buffer for short in/outputs.

## References
- https://git.kernel.org/stable/c/034e2d70b5c7f578200ad09955aeb2aa65d1164a
- https://git.kernel.org/stable/c/1291d278b5574819a7266568ce4c28bce9438705
- https://git.kernel.org/stable/c/1c0cf6d19690141002889d72622b90fc01562ce4
- https://git.kernel.org/stable/c/9e8ecd4908b53941ab6f0f51584ab80c6c6606c4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26789.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26789
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
