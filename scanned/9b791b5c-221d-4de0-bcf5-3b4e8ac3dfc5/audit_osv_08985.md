# [H] CVE-2016-7144

## Summary
Severity: High
Advisory: CVE-2016-7144
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-18
Source: https://osv.dev/vulnerability/CVE-2016-7144
Type: osv

## Details
The m_authenticate function in modules/m_sasl.c in UnrealIRCd before 3.2.10.7 and 4.x before 4.0.6 allows remote attackers to spoof certificate fingerprints and consequently log in as another user via a crafted AUTHENTICATE parameter.

## References
- http://www.openwall.com/lists/oss-security/2016/09/04/3
- http://www.openwall.com/lists/oss-security/2016/09/05/8
- http://www.securityfocus.com/bid/92763
- https://forums.unrealircd.org/viewtopic.php?f=1&t=8588
- https://github.com/unrealircd/unrealircd/commit/f473e355e1dc422c4f019dbf86bc50ba1a34a766
