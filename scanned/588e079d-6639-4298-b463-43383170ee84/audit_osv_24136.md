# [H] fs: jfs: fix shift-out-of-bounds in dbDiscardAG

## Summary
Severity: High
Advisory: CVE-2022-50333
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2022-50333
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs: jfs: fix shift-out-of-bounds in dbDiscardAG

This should be applied to most URSAN bugs found recently by syzbot,
by guarding the dbMount. As syzbot feeding rubbish into the bmap
descriptor.

## References
- https://git.kernel.org/stable/c/0183c8f46ab5bcd0740f41c87f5141c6ca2bf1bb
- https://git.kernel.org/stable/c/10b87da8fae79c7daf5eda6a9e4f1d31b85b4d92
- https://git.kernel.org/stable/c/25e70c6162f207828dd405b432d8f2a98dbf7082
- https://git.kernel.org/stable/c/3d340b684dcec5e34efc470227cd1c7d2df121ad
- https://git.kernel.org/stable/c/50163a115831ef4e6402db5a7ef487d1989d7249
- https://git.kernel.org/stable/c/624843f1bac448150f6859999c72c4841c14a2e3
- https://git.kernel.org/stable/c/911999b193735cd378517b6cd5fe585ee345d49c
- https://git.kernel.org/stable/c/ab5cd3d62c2493eca3337e7d0178cc7bd819ca64
- https://git.kernel.org/stable/c/f8d4d0bac603616e2fa4a3907e81ed13f8f3c380
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50333.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50333
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
