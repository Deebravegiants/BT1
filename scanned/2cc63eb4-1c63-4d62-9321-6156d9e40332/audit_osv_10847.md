# [M] CVE-2017-3226

## Summary
Severity: Medium
Advisory: CVE-2017-3226
CVSS: 6.4 (CVSS:3.0/AV:P/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-24
Source: https://osv.dev/vulnerability/CVE-2017-3226
Type: osv

## Details
Das U-Boot is a device bootloader that can read its configuration from an AES encrypted file. Devices that make use of Das U-Boot's AES-CBC encryption feature using environment encryption (i.e., setting the configuration parameter CONFIG_ENV_AES=y) read environment variables from disk as the encrypted disk image is processed. An attacker with physical access to the device can manipulate the encrypted environment data to include a crafted two-byte sequence which triggers an error in environment variable parsing. This error condition is improperly handled by Das U-Boot, resulting in an immediate process termination with a debugging message.

## References
- http://www.securityfocus.com/bid/100675
- https://www.kb.cert.org/vuls/id/166743
