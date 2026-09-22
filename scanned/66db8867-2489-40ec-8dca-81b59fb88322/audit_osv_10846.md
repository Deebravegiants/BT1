# [M] CVE-2017-3225

## Summary
Severity: Medium
Advisory: CVE-2017-3225
CVSS: 4.6 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-07-24
Source: https://osv.dev/vulnerability/CVE-2017-3225
Type: osv

## Details
Das U-Boot is a device bootloader that can read its configuration from an AES encrypted file. For devices utilizing this environment encryption mode, U-Boot's use of a zero initialization vector may allow attacks against the underlying cryptographic implementation and allow an attacker to decrypt the data. Das U-Boot's AES-CBC encryption feature uses a zero (0) initialization vector. This allows an attacker to perform dictionary attacks on encrypted data produced by Das U-Boot to learn information about the encrypted data.

## References
- http://www.securityfocus.com/bid/100675
- https://www.kb.cert.org/vuls/id/166743
