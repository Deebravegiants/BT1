# [H] misc: fastrpc: Fix copy buffer page size

## Summary
Severity: High
Advisory: CVE-2025-21734
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21734
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <6.1.129, >=6.2.0 <6.6.78, >=6.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: fastrpc: Fix copy buffer page size

For non-registered buffer, fastrpc driver copies the buffer and
pass it to the remote subsystem. There is a problem with current
implementation of page size calculation which is not considering
the offset in the calculation. This might lead to passing of
improper and out-of-bounds page size which could result in
memory issue. Calculate page start and page end using the offset
adjusted address instead of absolute address.

## References
- https://git.kernel.org/stable/c/24a79c6bc8de763f7c50f4f84f8b0c183bc25a51
- https://git.kernel.org/stable/c/c0464bad0e85fcd5d47e4297d1e410097c979e55
- https://git.kernel.org/stable/c/c3f7161123fcbdc64e90119ccce292d8b66281c4
- https://git.kernel.org/stable/c/c56ba3ea8e3c9a69a992aad18f7a65e43e51d623
- https://git.kernel.org/stable/c/e966eae72762ecfdbdb82627e2cda48845b9dd66
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21734.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21734
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
