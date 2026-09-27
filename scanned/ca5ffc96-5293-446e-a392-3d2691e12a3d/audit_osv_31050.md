# [H] jffs2: Prevent rtime decompress memory corruption

## Summary
Severity: High
Advisory: CVE-2024-57850
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-57850
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

jffs2: Prevent rtime decompress memory corruption

The rtime decompression routine does not fully check bounds during the
entirety of the decompression pass and can corrupt memory outside the
decompression buffer if the compressed data is corrupted. This adds the
required check to prevent this failure mode.

## References
- https://git.kernel.org/stable/c/421f9e9f0fae9f8e721ffa07f22d9765fa1214d5
- https://git.kernel.org/stable/c/47c9a7f81027a78afea9d2e9a54bfd8fabb6b3d0
- https://git.kernel.org/stable/c/6808a1812a3419542223e7fe9e2de577e99e45d1
- https://git.kernel.org/stable/c/bd384b04ad1995441b18fe6c1366d02de8c5d5eb
- https://git.kernel.org/stable/c/dc39b08fcc3831b0bc46add91ba93cd2aab50716
- https://git.kernel.org/stable/c/f6fc251baefc3cdc4f41f2f5a47940d7d4a67332
- https://git.kernel.org/stable/c/fe051552f5078fa02d593847529a3884305a6ffe
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57850.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57850
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
