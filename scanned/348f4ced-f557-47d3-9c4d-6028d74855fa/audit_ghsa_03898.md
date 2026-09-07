# [H] Signature validation bypass in XmlSecLibs

## Summary
Severity: High
Advisory: GHSA-pqm6-cgwr-x6pf
CVE: CVE-2019-3465
CWE: CWE-347
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-11-08
Source: https://github.com/advisories/GHSA-pqm6-cgwr-x6pf
Type: github-advisory

## Affected
- Packagist: `robrichards/xmlseclibs` — affected >=3.0.0 <3.0.4
- Packagist: `robrichards/xmlseclibs` — affected >=1.0.0 <2.1.1

## Details
Rob Richards XmlSecLibs, all versions prior to v3.0.3, as used for example by SimpleSAMLphp, performed incorrect validation of cryptographic signatures in XML messages, allowing an authenticated attacker to impersonate others or elevate privileges by creating a crafted XML message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3465
- https://github.com/robrichards/xmlseclibs/commit/0a53d3c3aa87564910cae4ed01416441d3ae0db5
- https://www.tenable.com/security/tns-2019-09
- https://www.debian.org/security/2019/dsa-4560
- https://simplesamlphp.org/security/201911-01
- https://seclists.org/bugtraq/2019/Nov/8
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XBSSRV5Q7JFCYO46A3EN624UZ4KXFQ2M
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OCSR3V6LNWJAD37VQB6M2K7P4RQSCVFG
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MAWOVYLZKYDCQBLQEJCFAAD3KQTBPHXE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HBE2SJSXG7J4XYLJ2H6HC2VPPOG2OMUN
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ESKJTWLE7QZBQ3EKMYXKMBQG3JDEJWM6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BNFMY5RRLU63P25HEBVDO5KAVI7TX7JV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BBKVDUZ7G5ZOUO4BFJWLNJ6VOKBQJX5U
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AB34ILMJ67CUROBOR6YPKB46VHXLOAJ4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7KID7C4AZPYYIZQIPSLANP4R2RQR6YK3
- https://lists.debian.org/debian-lts-announce/2019/11/msg00003.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/robrichards/xmlseclibs/CVE-2019-3465.yaml
