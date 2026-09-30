# [H] btrfs: fix extent map use-after-free when handling missing device in read_one_chunk

## Summary
Severity: High
Advisory: CVE-2022-50300
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2022-50300
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.15.87, >=5.16.0 <6.0.18, >=6.1.0 <6.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix extent map use-after-free when handling missing device in read_one_chunk

Store the error code before freeing the extent_map. Though it's
reference counted structure, in that function it's the first and last
allocation so this would lead to a potential use-after-free.

The error can happen eg. when chunk is stored on a missing device and
the degraded mount option is missing.

Bugzilla: https://bugzilla.kernel.org/show_bug.cgi?id=216721

## References
- https://git.kernel.org/stable/c/169a4cf46882974d4db6d85eb623ec898e51bbc0
- https://git.kernel.org/stable/c/1742e1c90c3da344f3bb9b1f1309b3f47482756a
- https://git.kernel.org/stable/c/b8e7ed42bc3ca0d0e4191ee394d34962d3624c22
- https://git.kernel.org/stable/c/fce3713197ebba239e1c7e02174ed216ea1ee014
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50300.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50300
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
