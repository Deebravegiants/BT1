# [H] udf: reject descriptors with oversized CRC length

## Summary
Severity: High
Advisory: CVE-2026-53369
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53369
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

udf: reject descriptors with oversized CRC length

udf_read_tagged() skips CRC verification when descCRCLength +
sizeof(struct tag) exceeds the block size.  A crafted UDF image can
set descCRCLength to an oversized value to bypass CRC validation
entirely; the descriptor is then accepted based solely on the 8-bit
tag checksum, which is trivially recomputable.

Reject such descriptors instead of silently accepting them.  A
legitimate single-block descriptor should never have a CRC length that
exceeds the block.

## References
- https://git.kernel.org/stable/c/1873eb81c65d3f849418d7386baa39c439c9fc38
- https://git.kernel.org/stable/c/31605bbe94557bff721eaf041001169d44ac6f98
- https://git.kernel.org/stable/c/3dede76d525919bb966f9213e131af685de5ff99
- https://git.kernel.org/stable/c/50dfaf4a027742b4fcdc3e9305e7199ece9bc6a6
- https://git.kernel.org/stable/c/55d41b0a20128e86b9e960dd2e3f0a2d69a18df7
- https://git.kernel.org/stable/c/7d1b6adbf90df6c8941090d5646fbeca25ba9770
- https://git.kernel.org/stable/c/832ab4a882dc9b3c0155490d9993642ef545fd22
- https://git.kernel.org/stable/c/fdb26e628d2a211a23815d375bd33bdf863344e2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53369.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53369
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
