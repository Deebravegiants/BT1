# [H] arm64: cacheinfo: Avoid out-of-bounds write to cacheinfo array

## Summary
Severity: High
Advisory: CVE-2025-21785
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21785
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: cacheinfo: Avoid out-of-bounds write to cacheinfo array

The loop that detects/populates cache information already has a bounds
check on the array size but does not account for cache levels with
separate data/instructions cache. Fix this by incrementing the index
for any populated leaf (instead of any populated level).

## References
- https://git.kernel.org/stable/c/4371ac7b494e933fffee2bd6265d18d73c4f05aa
- https://git.kernel.org/stable/c/4ff25f0b18d1d0174c105e4620428bcdc1213860
- https://git.kernel.org/stable/c/67b99a2b5811df4294c2ad50f9bff3b6a08bd618
- https://git.kernel.org/stable/c/715eb1af64779e1b1aa0a7b2ffb81414d9f708e5
- https://git.kernel.org/stable/c/875d742cf5327c93cba1f11e12b08d3cce7a88d2
- https://git.kernel.org/stable/c/88a3e6afaf002250220793df99404977d343db14
- https://git.kernel.org/stable/c/ab90894f33c15b14c1cee6959ab6c8dcb09127f8
- https://git.kernel.org/stable/c/e4fde33107351ec33f1a64188612fbc6ca659284
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21785.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21785
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
