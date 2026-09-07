# [H] Apache XML Graphics Batik Server-Side Request Forgery vulnerability

## Summary
Severity: High
Advisory: GHSA-gq5f-xv48-2365
CVE: CVE-2022-44729
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2023-08-22
Source: https://github.com/advisories/GHSA-gq5f-xv48-2365
Type: github-advisory

## Affected
- Maven: `org.apache.xmlgraphics:batik-bridge` — affected >=1.0 <1.17
- Maven: `org.apache.xmlgraphics:batik-svgrasterizer` — affected >=1.0 <1.17
- Maven: `org.apache.xmlgraphics:batik-transcoder` — affected >=1.0 <1.17

## Details
Server-Side Request Forgery (SSRF) vulnerability in Apache Software Foundation Apache XML Graphics Batik.This issue affects Apache XML Graphics Batik: 1.16.

On version 1.16, a malicious SVG could trigger loading external resources by default, causing resource consumption or in some cases even information disclosure. Users are recommended to upgrade to version 1.17 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-44729
- https://github.com/apache/xmlgraphics-batik/commit/85b3457d9902f64d5d409a8da060d5ba47d0b69b
- https://github.com/apache/xmlgraphics-batik/commit/aaa1dd3e6b5a7df781d73e0c37a1df6a8f318893
- https://github.com/apache/xmlgraphics-batik
- https://issues.apache.org/jira/browse/BATIK-1349
- https://lists.apache.org/thread/hco2nw1typoorz33qzs0fcdx0ws6d6j2
- https://lists.debian.org/debian-lts-announce/2023/10/msg00021.html
- https://security.gentoo.org/glsa/202401-11
- https://xmlgraphics.apache.org/security.html
- http://www.openwall.com/lists/oss-security/2023/08/22/2
- http://www.openwall.com/lists/oss-security/2023/08/22/4
