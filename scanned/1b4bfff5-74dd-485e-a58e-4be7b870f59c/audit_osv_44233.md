# [H] wifi: wcn36xx: fix OOB read from short trigger BA firmware response

## Summary
Severity: High
Advisory: CVE-2026-80635
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80635
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: wcn36xx: fix OOB read from short trigger BA firmware response

The firmware response length is only checked against sizeof(*rsp) (20
bytes), but when candidate_cnt >= 1, a 22-byte candidate struct is read
at buf + 20 without verifying the response contains it. This causes an
out-of-bounds read of stale heap data, corrupting the BA session state.

Add validation that the response includes the candidate data.

## References
- https://git.kernel.org/stable/c/04aba50212f9f274e1a726fb3873b5ce8da2d821
- https://git.kernel.org/stable/c/af8f0ea1f0a3a5fb5ed2b8fed3f1501d644597ee
- https://git.kernel.org/stable/c/b5e6f21923ca89d90256e7346301056f6502691e
- https://git.kernel.org/stable/c/c07aa0534d50361183833e3803204044cf1d0476
- https://git.kernel.org/stable/c/d0b57bcd0dac6e2c9a3e474ec280e7db0b3edf35
- https://git.kernel.org/stable/c/d0cafe6ed8d1f6d0097eda31d85f5760d4f359c2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80635.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80635
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
