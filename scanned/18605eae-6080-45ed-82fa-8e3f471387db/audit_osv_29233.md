# [H] fs/ntfs3: Validate ff offset

## Summary
Severity: High
Advisory: CVE-2024-41019
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41019
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.164, >=5.16.0 <6.1.102, >=6.2.0 <6.6.43, >=6.7.0 <6.9.12, >=6.10.0 <6.10.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Validate ff offset

This adds sanity checks for ff offset. There is a check
on rt->first_free at first, but walking through by ff
without any check. If the second ff is a large offset.
We may encounter an out-of-bound read.

## References
- https://git.kernel.org/stable/c/35652dfa8cc9a8a900ec0f1e0395781f94ffc5f0
- https://git.kernel.org/stable/c/50c47879650b4c97836a0086632b3a2e300b0f06
- https://git.kernel.org/stable/c/617cf144c206f98978ec730b17159344fd147cb4
- https://git.kernel.org/stable/c/6ae7265a7b816879fd0203e83b5030d3720bbb7a
- https://git.kernel.org/stable/c/818a257428644b8873e79c44404d8fb6598d4440
- https://git.kernel.org/stable/c/82c94e6a7bd116724738aa67eba6f5fedf3a3319
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41019.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41019
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
