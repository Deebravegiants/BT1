# [H] CVE-2023-52161

## Summary
Severity: High
Advisory: CVE-2023-52161
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-02-22
Source: https://osv.dev/vulnerability/CVE-2023-52161
Type: osv

## Details
The Access Point functionality in eapol_auth_key_handle in eapol.c in iNet wireless daemon (IWD) before 2.14 allows attackers to gain unauthorized access to a protected Wi-Fi network. An attacker can complete the EAPOL handshake by skipping Msg2/4 and instead sending Msg4/4 with an all-zero key.

## References
- https://iwd.wiki.kernel.org/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4KSGT4IZ23CJBOQA3AFYEMBJ5OHFZBMK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FOQ6VEE3CPJAQLMMGMLCYDGWHVG7UCJI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TL2CFNWBL2E6AT2SIY2PR3IAWVCDYJZQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZZTPXEPTMASG37NDGAQMH2OTM6OPIP5A/
- https://lists.debian.org/debian-lts-announce/2024/02/msg00008.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AYRPQ3OLV3GGLUCDYWBHU34DLBLM62XJ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4KSGT4IZ23CJBOQA3AFYEMBJ5OHFZBMK/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FOQ6VEE3CPJAQLMMGMLCYDGWHVG7UCJI/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TL2CFNWBL2E6AT2SIY2PR3IAWVCDYJZQ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZZTPXEPTMASG37NDGAQMH2OTM6OPIP5A/
- https://www.top10vpn.com/research/wifi-vulnerabilities/
- https://git.kernel.org/pub/scm/network/wireless/iwd.git/commit/?id=6415420f1c92012f64063c131480ffcef58e60ca
