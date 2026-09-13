# [H] firmware: cs_dsp: Use strnlen() on name fields in V1 wmfw files

## Summary
Severity: High
Advisory: CVE-2024-41056
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41056
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.100, >=6.2.0 <6.6.41, >=6.7.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: cs_dsp: Use strnlen() on name fields in V1 wmfw files

Use strnlen() instead of strlen() on the algorithm and coefficient name
string arrays in V1 wmfw files.

In V1 wmfw files the name is a NUL-terminated string in a fixed-size
array. cs_dsp should protect against overrunning the array if the NUL
terminator is missing.

## References
- https://git.kernel.org/stable/c/16d76857d6b5426f41b587d0bb925de3f25bfb21
- https://git.kernel.org/stable/c/392cff2f86a25a4286ff3151c7739143c61c1781
- https://git.kernel.org/stable/c/53a9f8cdbf35a682e9894e1a606f4640e5359185
- https://git.kernel.org/stable/c/680e126ec0400f6daecf0510c5bb97a55779ff03
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41056.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41056
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
