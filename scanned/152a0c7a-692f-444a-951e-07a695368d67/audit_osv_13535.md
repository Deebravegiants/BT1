# [M] CVE-2018-20187

## Summary
Severity: Medium
Advisory: CVE-2018-20187
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-03-08
Source: https://osv.dev/vulnerability/CVE-2018-20187
Type: osv

## Details
A side-channel issue was discovered in Botan before 2.9.0. An attacker capable of precisely measuring the time taken for ECC key generation may be able to derive information about the high bits of the secret key, as the function to derive the public point from the secret scalar uses an unblinded Montgomery ladder whose loop iteration count depends on the bitlength of the secret. This issue affects only key generation, not ECDSA signatures or ECDH key agreement.

## References
- https://botan.randombit.net/news.html
- https://botan.randombit.net/security.html
- https://github.com/crocs-muni/ECTester
