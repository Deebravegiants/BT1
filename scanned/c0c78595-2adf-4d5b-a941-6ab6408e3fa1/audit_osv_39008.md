# [C] net/ipv6: ioam6: prevent schema length wraparound in trace fill

## Summary
Severity: Critical
Advisory: CVE-2026-43341
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43341
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.210, >=5.16.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/ipv6: ioam6: prevent schema length wraparound in trace fill

ioam6_fill_trace_data() stores the schema contribution to the trace
length in a u8. With bit 22 enabled and the largest schema payload,
sclen becomes 1 + 1020 / 4, wraps from 256 to 0, and bypasses the
remaining-space check. __ioam6_fill_trace_data() then positions the
write cursor without reserving the schema area but still copies the
4-byte schema header and the full schema payload, overrunning the trace
buffer.

Keep sclen in an unsigned int so the remaining-space check and the write
cursor calculation both see the full schema length.

## References
- https://git.kernel.org/stable/c/184d2e9db27c0f76226b5cad16fe29510a5d2280
- https://git.kernel.org/stable/c/5e67ba9bb531e1ec6599a82a065dea9040b9ce50
- https://git.kernel.org/stable/c/77695a69baca9b99d95fad09fc78c2318736604f
- https://git.kernel.org/stable/c/d1b041080086e91d3733a5438a8c51ad5d3d8e09
- https://git.kernel.org/stable/c/d3a1fb2ca323d7a4e10ab3afbfa25e6d8921e4f2
- https://git.kernel.org/stable/c/d6e1c9b02d85a4f1f4ba6d68e916d9b610a3ed7d
- https://git.kernel.org/stable/c/e96d48b37708d53cbdc47f6f60b0714fc4a5f596
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43341.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43341
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
