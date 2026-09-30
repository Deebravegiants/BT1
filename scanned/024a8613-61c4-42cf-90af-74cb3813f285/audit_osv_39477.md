# [H] slip: bound decode() reads against the compressed packet length

## Summary
Severity: High
Advisory: CVE-2026-45843
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45843
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

slip: bound decode() reads against the compressed packet length

slhc_uncompress() parses a VJ-compressed TCP header by advancing a
pointer through the packet via decode() and pull16(). Neither helper
bounds-checks against isize, and decode() masks its return with
& 0xffff so it can never return the -1 that callers test for -- those
error paths are dead code.

A short compressed frame whose change byte requests optional fields
lets decode() read past the end of the packet. The over-read bytes
are folded into the cached cstate and reflected into subsequent
reconstructed packets.

Make decode() and pull16() take the packet end pointer and return -1
when exhausted. Add a bounds check before the TCP-checksum read.
The existing == -1 tests now do what they were always meant to.

## References
- https://git.kernel.org/stable/c/0511ecb00e61bf28e2fec4bb41fcce385c3a3b2d
- https://git.kernel.org/stable/c/335957df4ed60f02a2ec0432fbedbf0cc7241d8b
- https://git.kernel.org/stable/c/37537e42e6df387398bee85cb85070cc80bb1e10
- https://git.kernel.org/stable/c/4c1367a2d7aad643a6f87c6931b13cc1a25e8ca7
- https://git.kernel.org/stable/c/4cefe32639933d652614b0bd50f818f9af4af78f
- https://git.kernel.org/stable/c/6268f01ae989013671b526c883e92655342c6f6f
- https://git.kernel.org/stable/c/9aafba2f49e1fcccc2018816f5836a609c925879
- https://git.kernel.org/stable/c/d42bec6e4f6d6d658be365539400b3314b76b2a7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45843.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45843
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
