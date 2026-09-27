# [H] crypto: af_alg - Cap AEAD AD length to 0x80000000

## Summary
Severity: High
Advisory: CVE-2026-52972
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52972
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10, >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: af_alg - Cap AEAD AD length to 0x80000000

In order to prevent arithmetic overflows when checking the TX
buffer size, cap the associated data length to 0x80000000.

## References
- https://git.kernel.org/stable/c/0b3a57d218618cb1cc78ddc9ba02c07de84b46f4
- https://git.kernel.org/stable/c/265ac26d1c5e17b34d497cbda1f754a1ec8552bc
- https://git.kernel.org/stable/c/97948906dc8e0ea84775e03e35b60a2063c70193
- https://git.kernel.org/stable/c/a1c5672faf8e93e38c2deac3979cc767ca5cf918
- https://git.kernel.org/stable/c/a4fe4eb580bbc7439f649a496d4cf38415a4021c
- https://git.kernel.org/stable/c/a9f68d9ed38dd6e5a6c6d75b03d25c1c133e321d
- https://git.kernel.org/stable/c/e4c06479d7059888adf2f22bc1ebcf053bf691a2
- https://git.kernel.org/stable/c/e4c4a5074532eaaa14951994a3aad0d479aa7431
- https://git.kernel.org/stable/c/f8a5203596797f394ff3f9aa4005597a92249802
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-52972.json
- https://access.redhat.com/security/cve/CVE-2026-52972
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52972.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52972
- https://bugzilla.redhat.com/show_bug.cgi?id=2492364
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
