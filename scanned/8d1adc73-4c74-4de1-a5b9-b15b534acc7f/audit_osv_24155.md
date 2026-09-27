# [M] brcmfmac: return error when getting invalid max_flowrings from dongle

## Summary
Severity: Medium
Advisory: CVE-2022-50358
Ecosystem: Linux
CVSS: 4.2 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2022-50358
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.17.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

brcmfmac: return error when getting invalid max_flowrings from dongle

When firmware hit trap at initialization, host will read abnormal
max_flowrings number from dongle, and it will cause kernel panic when
doing iowrite to initialize dongle ring.
To detect this error at early stage, we directly return error when getting
invalid max_flowrings(>256).

## References
- https://git.kernel.org/stable/c/10c4b63d09a5b0ebf1b61af1dae7f25555cf58b6
- https://git.kernel.org/stable/c/200347eb3b2608cc8b54c13dd1d5e03809ba2eb2
- https://git.kernel.org/stable/c/2aca4f3734bd717e04943ddf340d49ab62299a00
- https://git.kernel.org/stable/c/2e8bb402b060a6c22160de3d72cee057698177c8
- https://git.kernel.org/stable/c/3cc9299036bdb647408e11e41de3eb1ff6d428cd
- https://git.kernel.org/stable/c/87f126b25fa8562196f0f4c0aa46a446026199bf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50358.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50358
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
