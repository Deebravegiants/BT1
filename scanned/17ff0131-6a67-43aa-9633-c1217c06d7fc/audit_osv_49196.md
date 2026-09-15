# [M] CVE-2018-5383

## Summary
Severity: Medium
Advisory: CVE-2018-5383
CVSS: 6.8 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-08-07
Source: https://osv.dev/vulnerability/CVE-2018-5383
Type: osv

## Details
Bluetooth firmware or operating system software drivers in macOS versions before 10.13, High Sierra and iOS versions before 11.4, and Android versions before the 2018-06-05 patch may not sufficiently validate elliptic curve parameters used to generate public keys during a Diffie-Hellman key exchange, which may allow a remote attacker to obtain the encryption key used by the device.

## References
- https://usn.ubuntu.com/4094-1/
- https://usn.ubuntu.com/4095-2/
- https://usn.ubuntu.com/4118-1/
- https://www.bluetooth.com/news/unknown/2018/07/bluetooth-sig-security-update
- https://www.kb.cert.org/vuls/id/304725
- http://www.cs.technion.ac.il/~biham/BT/
- http://www.securityfocus.com/bid/104879
- https://access.redhat.com/errata/RHSA-2019:2169
- https://usn.ubuntu.com/4095-1/
- https://usn.ubuntu.com/4351-1/
- http://www.securitytracker.com/id/1041432
- https://lists.debian.org/debian-lts-announce/2019/04/msg00005.html
