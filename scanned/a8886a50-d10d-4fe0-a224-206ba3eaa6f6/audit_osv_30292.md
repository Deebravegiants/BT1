# [M] media: v4l2-tpg: prevent the risk of a division by zero

## Summary
Severity: Medium
Advisory: CVE-2024-50287
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50287
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <4.19.324, >=4.20.0 <5.4.286, >=5.5.0 <5.10.230, >=5.11.0 <5.15.172, >=5.16.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: v4l2-tpg: prevent the risk of a division by zero

As reported by Coverity, the logic at tpg_precalculate_line()
blindly rescales the buffer even when scaled_witdh is equal to
zero. If this ever happens, this will cause a division by zero.

Instead, add a WARN_ON_ONCE() to trigger such cases and return
without doing any precalculation.

## References
- https://git.kernel.org/stable/c/054931ca3cfcb8e8fa036e887d6f379942b02565
- https://git.kernel.org/stable/c/0bfc6e38ee2250f0503d96f1a1de441c31d88715
- https://git.kernel.org/stable/c/0cdb42ba0b28f548c1a4e86bb8489dba0d78fc21
- https://git.kernel.org/stable/c/2d0f01aa602fd15a805771bdf3f4d9a9b4df7f47
- https://git.kernel.org/stable/c/a749c15dccc58d9cbad9cd23bd8ab4b5fa96cf47
- https://git.kernel.org/stable/c/c63c30c9d9f2c8de34b16cd2b8400240533b914e
- https://git.kernel.org/stable/c/e3c36d0bde309f690ed1f9cd5f7e63b3a513f94a
- https://git.kernel.org/stable/c/e6a3ea83fbe15d4818d01804e904cbb0e64e543b
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50287.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50287
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
