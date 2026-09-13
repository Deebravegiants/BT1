# [H] s390/zcrypt: Validate length for CCA ECC private key requests

## Summary
Severity: High
Advisory: CVE-2026-68451
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-68451
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/zcrypt: Validate length for CCA ECC private key requests

cca_ecc2protkey() derives the copy length for the CPRB parameter
block directly from the length field in the key token. Reject the
request early if the token length exceeds the available space in the
parameter block.

## References
- https://git.kernel.org/stable/c/013a4484f061a2b41f052e25c0015203287e63f1
- https://git.kernel.org/stable/c/447a37a6bef11bfd3645069e380460b11386e2b9
- https://git.kernel.org/stable/c/7dc306ff7c4d951582adaae65e0aee9fb4968dbe
- https://git.kernel.org/stable/c/8fa3e9435a13c335efb63fb4f4e77531a0031159
- https://git.kernel.org/stable/c/a9ae0f6dd45c3ccc1d69363f7aea8af179122730
- https://git.kernel.org/stable/c/dd25bd9b0f36849808bd7625dcc59dd4c1aeef3e
- https://git.kernel.org/stable/c/ecc3b8691c1935f9f3e4eb964ab11e40fdec17f5
- https://git.kernel.org/stable/c/f0831f13c42c1261d449dcee8a035e1c6cd9fcaa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68451.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68451
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
