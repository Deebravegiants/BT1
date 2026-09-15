# [H] s390/zcrypt: Validate length for CCA AES cipher key requests

## Summary
Severity: High
Advisory: CVE-2026-68452
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-68452
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/zcrypt: Validate length for CCA AES cipher key requests

cca_cipher2protkey() derives the copy length for the CPRB parameter
block directly from the length field in the key token. Reject the
request early if the token length exceeds the available space in the
parameter block.

## References
- https://git.kernel.org/stable/c/06afe425d5283b9764303de47f554da5a808ce8a
- https://git.kernel.org/stable/c/3859f630b674801a00bca39bc451f52288591f65
- https://git.kernel.org/stable/c/406b317ea2b501f6f5eca1264293c9399a73a778
- https://git.kernel.org/stable/c/4e500ecb6704d879f9c2417c2ed6faba595015ca
- https://git.kernel.org/stable/c/4fc46deceda076d429ef3fab2ccf8d96629ebd23
- https://git.kernel.org/stable/c/7f9e5a3dbb14a9b321a1dfa30390402c673f82dc
- https://git.kernel.org/stable/c/ad93a1f1a45652478c0cf4eb029114e03af57f3b
- https://git.kernel.org/stable/c/be037204e4f595e4bd2159acda146677a1dc6342
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68452.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68452
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
