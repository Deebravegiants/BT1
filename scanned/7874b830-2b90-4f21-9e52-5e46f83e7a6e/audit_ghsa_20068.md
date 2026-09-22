# [M] golang.org/x/net/http2 vulnerable to possible excessive memory growth

## Summary
Severity: Medium
Advisory: GHSA-xrjj-mj9h-534m
CVE: CVE-2022-41717
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-12-08
Source: https://github.com/advisories/GHSA-xrjj-mj9h-534m
Type: github-advisory

## Affected
- Go: `golang.org/x/net/http2` — affected >=0 <0.4.0
- Go: `golang.org/x/net` — affected >=0 <0.4.0

## Details
An attacker can cause excessive memory growth in a Go server accepting HTTP/2 requests. HTTP/2 server connections contain a cache of HTTP header keys sent by the client. While the total number of entries in this cache is capped, an attacker sending very large keys can cause the server to allocate approximately 64 MiB per open connection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41717
- https://security.gentoo.org/glsa/202311-09
- https://pkg.go.dev/vuln/GO-2022-1144
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZSVEMQV5ROY5YW5QE3I57HT3ITWG5GCV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WPEIZ7AMEJCZXU3FEJZMVRNHQZXX5P3I
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/T7N5GV4CHH6WAGX3GFMDD3COEOVCZ4RI
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/REMHVVIBDNKSRKNOTV7EQSB7CYQWOUOU
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QBKBAZBIOXZV5QCFHZNSVXULR32XJCYD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Q52IQI754YAE4XPR4QBRWPIVZWYGZ4FS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PW3XC47AUW5J5M2ULJX7WCCL3B2ETLMT
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PUM4DIVOLJCBK5ZDP4LJOL24GXT3YSIR
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NQGNAXK3YBPMUP3J4TECIRDHFGW37522
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KEOTKBUPZXHE3F352JBYNTSNRXYLWD6P
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CSVIS6MTMFVBA7JPMRAUNKUOYEVSJYSB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CHHITS4PUOZAKFIUBQAQZC7JWXMOYE4B
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ANIOPUXWIHVRA6CEWXCGOMX3YYS6KFHG
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5RSKA2II6QTD4YUKUNDVJQSRYSFC4VFR
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/56B2FFESRYYP6IY2AZ3UWXLWKZ5IYZN4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4SBIUECMLNC572P23DDOKJNKPJVX26SP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4BUK2ZIAGCULOOYDNH25JPU6JBES5NF2
