# [H] speakup: Avoid crash on very long word

## Summary
Severity: High
Advisory: CVE-2024-26994
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26994
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.37 <4.19.313, >=4.20.0 <5.4.275, >=5.5.0 <5.10.216, >=5.11.0 <5.15.157, >=5.16.0 <6.1.88, >=6.2.0 <6.6.29, >=6.7.0 <6.8.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

speakup: Avoid crash on very long word

In case a console is set up really large and contains a really long word
(> 256 characters), we have to stop before the length of the word buffer.

## References
- https://git.kernel.org/stable/c/0d130158db29f5e0b3893154908cf618896450a8
- https://git.kernel.org/stable/c/0efb15c14c493263cb3a5f65f5ddfd4603d19a76
- https://git.kernel.org/stable/c/6401038acfa24cba9c28cce410b7505efadd0222
- https://git.kernel.org/stable/c/756c5cb7c09e537b87b5d3acafcb101b2ccf394f
- https://git.kernel.org/stable/c/89af25bd4b4bf6a71295f07e07a8ae7dc03c6595
- https://git.kernel.org/stable/c/8defb1d22ba0395b81feb963b96e252b097ba76f
- https://git.kernel.org/stable/c/8f6b62125befe1675446923e4171eac2c012959c
- https://git.kernel.org/stable/c/c8d2f34ea96ea3bce6ba2535f867f0d4ee3b22e1
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4EZ6PJW7VOZ224TD7N4JZNU6KV32ZJ53/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DAMSOZXJEPUOXW33WZYWCVAY7Z5S7OOY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GCBZZEC7L7KTWWAS2NLJK6SO3IZIL4WW/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26994.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26994
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
