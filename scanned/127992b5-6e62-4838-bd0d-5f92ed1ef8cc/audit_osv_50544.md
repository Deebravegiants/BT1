# [M] CVE-2020-1774

## Summary
Severity: Medium
Advisory: CVE-2020-1774
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-04-28
Source: https://osv.dev/vulnerability/CVE-2020-1774
Type: osv

## Details
When user downloads PGP or S/MIME keys/certificates, exported file has same name for private and public keys. Therefore it's possible to mix them and to send private key to the third-party instead of public key. This issue affects ((OTRS)) Community Edition: 5.0.42 and prior versions, 6.0.27 and prior versions. OTRS: 7.0.16 and prior versions.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00040.html
- https://otrs.com/release-notes/otrs-security-advisory-2020-11/
- https://lists.debian.org/debian-lts-announce/2020/05/msg00000.html
