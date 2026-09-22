# [C] libceph: reject zero bucket types in crush_decode

## Summary
Severity: Critical
Advisory: CVE-2026-68154
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68154
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: reject zero bucket types in crush_decode

CRUSH bucket type 0 is reserved for devices.  The mapper relies on
that invariant and uses type 0 to identify leaf devices.

If crush_decode() accepts a bucket with type 0, a malformed CRUSH map
can make the mapper treat a negative bucket ID as a device and pass it
to is_out(), which then indexes the OSD weight array with a negative
value.

Reject zero bucket types while decoding the CRUSH map so the invalid
state never reaches the mapper.

## References
- https://git.kernel.org/stable/c/05f90284223381005d6bcddab3fda4a97f9c3401
- https://git.kernel.org/stable/c/146461f09565afe3665e65b0423d3d6b0fe806c5
- https://git.kernel.org/stable/c/3b2f1937f5fce8b7dd5432e7693e3cc8b5eece56
- https://git.kernel.org/stable/c/70998f91030ee083ecb336a1dff0701c20a38081
- https://git.kernel.org/stable/c/80fc40e11cda1b5d990a3f69c6efa344fb5cd987
- https://git.kernel.org/stable/c/826cd1de5802fd392922785f9b64d76e65d2a100
- https://git.kernel.org/stable/c/952ca5dc99913d169263f59fd689f586729a13c1
- https://git.kernel.org/stable/c/b8a9fb6bf806f9c4891e71ae1beab0c07c23a877
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68154.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68154
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
