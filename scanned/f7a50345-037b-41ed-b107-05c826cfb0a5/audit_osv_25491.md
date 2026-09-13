# [H] Incorrect Authentication Tag length usage in AES GCM decryption in OpenIDC/cjose

## Summary
Severity: High
Advisory: CVE-2023-37464
Aliases: GHSA-3rhg-3gf2-6xgj
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2023-07-14
Source: https://osv.dev/vulnerability/CVE-2023-37464
Type: osv

## Details
OpenIDC/cjose is a C library implementing the Javascript Object Signing and Encryption (JOSE). The AES GCM decryption routine incorrectly uses the Tag length from the actual Authentication Tag provided in the JWE. The spec  says that a fixed length of 16 octets must be applied. Therefore this bug allows an attacker to provide a truncated Authentication Tag and to modify the JWE accordingly. Users should upgrade to a version >= 0.6.2.2. Users unable to upgrade should avoid using AES GCM encryption and replace it with another encryption algorithm (e.g. AES CBC).

## References
- https://datatracker.ietf.org/doc/html/rfc7518#section-4.7
- https://github.com/OpenIDC/cjose/releases/tag/v0.6.2.2
- https://lists.debian.org/debian-lts-announce/2023/08/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DFWAPMYYVBO2U65HPYDTBEKNSXG4TP5C/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LCQJXKDPCWCXB2V4JMQ3UWYJ4UIBPUW6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PTZHOVGY7AHGNMEY245HK4Q36AMA53AL/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37464.json
- https://github.com/OpenIDC/cjose/security/advisories/GHSA-3rhg-3gf2-6xgj
- https://nvd.nist.gov/vuln/detail/CVE-2023-37464
- https://www.debian.org/security/2023/dsa-5472
- https://github.com/OpenIDC/cjose/commit/7325e9a5e71e2fc0e350487ecac7d84acdf0ed5e
