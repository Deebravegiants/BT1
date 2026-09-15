# [M] drm/msm/mdp5: Don't leak some plane state

## Summary
Severity: Medium
Advisory: CVE-2023-53324
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53324
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <4.19.295, >=4.20.0 <5.4.257, >=5.5.0 <5.10.195, >=5.11.0 <5.15.132, >=5.16.0 <6.1.53, >=6.2.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/mdp5: Don't leak some plane state

Apparently no one noticed that mdp5 plane states leak like a sieve
ever since we introduced plane_state->commit refcount a few years ago
in 21a01abbe32a ("drm/atomic: Fix freeing connector/plane state too
early by tracking commits, v3.")

Fix it by using the right helpers.

Patchwork: https://patchwork.freedesktop.org/patch/551236/

## References
- https://git.kernel.org/stable/c/12dfd02cbd1a678fbd66be0c2f79d5299c4921a9
- https://git.kernel.org/stable/c/2965015006ef18ca96d2eab9ebe6bca884c63291
- https://git.kernel.org/stable/c/5b0dd3a102f64996598bd1e8d8388848a7c561bc
- https://git.kernel.org/stable/c/7fc11a830b2eb07a0e3c6f917e5e636df6fc5d4c
- https://git.kernel.org/stable/c/815e42029f6e1e762898079f85546d6a0391ab95
- https://git.kernel.org/stable/c/b8a61df6f40448cf46611f7af05b00970d08d620
- https://git.kernel.org/stable/c/c0b1eee648702e04f1005d451f9689575b7f52ed
- https://git.kernel.org/stable/c/fd0ad3b2365c1c58aa5a761c18efc4817193beb6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53324.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53324
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
