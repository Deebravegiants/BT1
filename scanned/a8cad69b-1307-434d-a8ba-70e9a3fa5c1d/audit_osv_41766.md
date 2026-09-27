# [H] KEYS: fix overflow in keyctl_pkey_params_get_2()

## Summary
Severity: High
Advisory: CVE-2026-63824
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63824
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.260, >=5.11.0 <5.15.211, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

KEYS: fix overflow in keyctl_pkey_params_get_2()

The length for the internal output buffer is calculated incorrectly, which
can result overflow when a too small buffer is provided.

Fix the bug by allocating internal output with the size of the maximum
length of the cryptographic primitive instead of caller provided size.

## References
- https://git.kernel.org/stable/c/0f3058d7d26f81df9b68a18ddbe164bdc3c5eff3
- https://git.kernel.org/stable/c/5165f1cc727f1322456735df212d8e26ec237a8d
- https://git.kernel.org/stable/c/5966e4e2ba213ab7ad559166152eb4f1f170dd2c
- https://git.kernel.org/stable/c/622ec2dcd59f21623f2a7ab773c80ceb7d555e3a
- https://git.kernel.org/stable/c/670fc6a311ed321522b7fff92cf0fc376b4f6e78
- https://git.kernel.org/stable/c/b11c1fa32667692a2c0566e10163758e786e430c
- https://git.kernel.org/stable/c/b1e247338bc71826a2d2def3e0874c34749df69a
- https://git.kernel.org/stable/c/cb481e59ea6cae3b7796ac1d7a22b6b24c3f3c0b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63824.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63824
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
