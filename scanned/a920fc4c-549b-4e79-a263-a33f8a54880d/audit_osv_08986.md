# [C] CVE-2016-7145

## Summary
Severity: Critical
Advisory: CVE-2016-7145
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-07
Source: https://osv.dev/vulnerability/CVE-2016-7145
Type: osv

## Details
The m_authenticate function in ircd/m_authenticate.c in nefarious2 allows remote attackers to spoof certificate fingerprints and consequently log in as another user via a crafted AUTHENTICATE parameter.

## References
- http://www.openwall.com/lists/oss-security/2016/09/05/9
- https://github.com/evilnet/nefarious2/commit/f50a84bad996d438e7b31b9e74c32a41e43f8be5
