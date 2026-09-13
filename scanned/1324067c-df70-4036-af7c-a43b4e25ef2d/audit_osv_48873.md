# [M] CVE-2018-16758

## Summary
Severity: Medium
Advisory: CVE-2018-16758
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-10-10
Source: https://osv.dev/vulnerability/CVE-2018-16758
Type: osv

## Details
Missing message authentication in the meta-protocol in Tinc VPN version 1.0.34 and earlier allows a man-in-the-middle attack to disable the encryption of VPN packets.

## References
- http://www.tinc-vpn.org/git/browse?p=tinc%3Ba=commit%3Bh=e97943b7cc9c851ae36f5a41e2b6102faa74193f
- http://tinc-vpn.org/security/
- https://www.debian.org/security/2018/dsa-4312
- https://www.starwindsoftware.com/security/sw-20190227-0003/
