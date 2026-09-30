# [H] CVE-2016-7143

## Summary
Severity: High
Advisory: CVE-2016-7143
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/CVE-2016-7143
Type: osv

## Details
The m_authenticate function in modules/m_sasl.c in Charybdis before 3.5.3 allows remote attackers to spoof certificate fingerprints and consequently log in as another user via a crafted AUTHENTICATE parameter.

## References
- http://www.securityfocus.com/bid/92761
- http://www.debian.org/security/2016/dsa-3661
- http://www.openwall.com/lists/oss-security/2016/09/04/3
- http://www.openwall.com/lists/oss-security/2016/09/05/8
- https://github.com/charybdis-ircd/charybdis/blob/charybdis-3.5.3/NEWS.md
- https://github.com/charybdis-ircd/charybdis/commit/818a3fda944b26d4814132cee14cfda4ea4aa824
