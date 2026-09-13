# [H] drivers: media: dvb-frontends/rtl2830: fix an out-of-bounds write error

## Summary
Severity: High
Advisory: CVE-2024-47697
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47697
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drivers: media: dvb-frontends/rtl2830: fix an out-of-bounds write error

Ensure index in rtl2830_pid_filter does not exceed 31 to prevent
out-of-bounds access.

dev->filters is a 32-bit value, so set_bit and clear_bit functions should
only operate on indices from 0 to 31. If index is 32, it will attempt to
access a non-existent 33rd bit, leading to out-of-bounds access.
Change the boundary check from index > 32 to index >= 32 to resolve this
issue.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/042b101d7bf70616c4967c286ffa6fcca65babfb
- https://git.kernel.org/stable/c/3dba83d3c81de1368d15a39f22df7b53e306052f
- https://git.kernel.org/stable/c/46d7ebfe6a75a454a5fa28604f0ef1491f9d8d14
- https://git.kernel.org/stable/c/58f31be7dfbc0c84a6497ad51924949cf64b86a2
- https://git.kernel.org/stable/c/7fd6aae7e53b94f4035b1bfce28b8dfa0d0ae470
- https://git.kernel.org/stable/c/86d920d2600c3a48efc2775c1666c1017eec6956
- https://git.kernel.org/stable/c/883f794c6e498ae24680aead55c16f66b06cfc30
- https://git.kernel.org/stable/c/8ffbe7d07b8e76193b151107878ddc1ccc94deb5
- https://git.kernel.org/stable/c/badbd736e6649c4e6d7b4ff7e2b9857acfa9ea94
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47697.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47697
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
