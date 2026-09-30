# [H] jquery-plugin-query-object contains prototype pollution vulnerability

## Summary
Severity: High
Advisory: GHSA-q9xg-h756-8689
CVE: CVE-2021-20083
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q9xg-h756-8689
Type: github-advisory

## Affected
- npm: `jquery-query-object` — affected >=0

## Details
Improperly Controlled Modification of Object Prototype Attributes ('Prototype Pollution') in jquery-plugin-query-object 2.2.3 allows a malicious user to inject properties into Object.prototype.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20083
- https://github.com/BlackFan/client-side-prototype-pollution/blob/master/pp/jquery-query-object.md
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7CR6VGITIB2TXXZ6B5QRRWPU5S4BXQPD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IJX6NVXSRN3RX3YUVEJQ4WUTQSDL3DSR
- http://packetstormsecurity.com/files/166299/WordPress-Core-5.9.0-5.9.1-Cross-Site-Scripting.html
