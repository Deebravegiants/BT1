# [H] In libexpat through 2.4.9, there is a use-after free caused by overeager destruction of a shared DTD...

## Summary
Severity: High
Advisory: JLSEC-2025-58
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-14
Source: https://osv.dev/vulnerability/JLSEC-2025-58
Type: osv

## Affected
- Julia: `Expat_jll` — affected >=0 <2.5.0+0

## Details
In libexpat through 2.4.9, there is a use-after free caused by overeager destruction of a shared DTD in `XML_ExternalEntityParserCreate` in out-of-memory situations.

## References
- http://www.openwall.com/lists/oss-security/2023/12/28/5
- http://www.openwall.com/lists/oss-security/2024/01/03/5
- https://github.com/libexpat/libexpat/issues/649
- https://github.com/libexpat/libexpat/pull/616
- https://github.com/libexpat/libexpat/pull/650
- https://lists.debian.org/debian-lts-announce/2022/10/msg00033.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AJ5VY2VYXE4WTRGQ6LMGLF6FV3SY37YE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BY4OPSIB33ETNUXZY2UPZ4NGQ3OKDY4D/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DPQVIF6TOJNY2T3ZZETFKR4G34FFREBQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FFCOMBSOJKLIKCGCJWHLJXO4EVYBG7AR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IUJ2BULJTZ2BMSKQHB6US674P55UCWWS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XG5XOOB7CD55CEE6OJYKSACSIMQ4RWQ6/
- https://security.gentoo.org/glsa/202210-38
- https://security.netapp.com/advisory/ntap-20221118-0007/
- https://www.debian.org/security/2022/dsa-5266
