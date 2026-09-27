# [H] fpga: prevent integer overflow in dfl_feature_ioctl_set_irq()

## Summary
Severity: High
Advisory: CVE-2022-50623
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2022-50623
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

fpga: prevent integer overflow in dfl_feature_ioctl_set_irq()

The "hdr.count * sizeof(s32)" multiplication can overflow on 32 bit
systems leading to memory corruption.  Use array_size() to fix that.

## References
- https://git.kernel.org/stable/c/1b5a931594f7ffd26d706614c37d4da0f2ffb6e7
- https://git.kernel.org/stable/c/939bc5453b8cbdde9f1e5110ce8309aedb1b501a
- https://git.kernel.org/stable/c/940253af8b3865b76de8d1b46bcd4a700104852e
- https://git.kernel.org/stable/c/b94605f5cb99e90c8ca91523597a40e1bd59546b
- https://git.kernel.org/stable/c/f59861946fa51bcc1f305809e4ebc1013b0ee61c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50623.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50623
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
