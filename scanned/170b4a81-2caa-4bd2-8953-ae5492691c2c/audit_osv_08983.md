# [M] CVE-2016-7142

## Summary
Severity: Medium
Advisory: CVE-2016-7142
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-09-26
Source: https://osv.dev/vulnerability/CVE-2016-7142
Type: osv

## Details
The m_sasl module in InspIRCd before 2.0.23, when used with a service that supports SASL_EXTERNAL authentication, allows remote attackers to spoof certificate fingerprints and consequently log in as another user via a crafted SASL message.

## References
- http://www.openwall.com/lists/oss-security/2016/09/04/3
- http://www.debian.org/security/2016/dsa-3662
- http://www.inspircd.org/2016/09/03/v2023-released.html
- http://www.openwall.com/lists/oss-security/2016/09/05/8
- https://github.com/inspircd/inspircd/commit/74fafb7f11b06747f69f182ad5e3769b665eea7a
