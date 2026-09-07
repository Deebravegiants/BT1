# [M] Apache CXF is vulnerable to DoS attacks as entire files are read into memory and logged

## Summary
Severity: Medium
Advisory: GHSA-36wv-v2qp-v4g4
CVE: CVE-2025-48795
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-07-15
Source: https://github.com/advisories/GHSA-36wv-v2qp-v4g4
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-core` — affected >=0 <3.5.11
- Maven: `org.apache.cxf:cxf-core` — affected >=3.6.0 <3.6.6
- Maven: `org.apache.cxf:cxf-core` — affected >=4.0.0 <4.0.7
- Maven: `org.apache.cxf:cxf-core` — affected >=4.1.0 <4.1.1

## Details
Apache CXF stores large stream based messages as temporary files on the local filesystem. A bug was introduced which means that the entire temporary file is read into memory and then logged. An attacker might be able to exploit this to cause a denial of service attack by causing an out of memory exception. In addition, it is possible to configure CXF to encrypt temporary files to prevent sensitive credentials from being cached unencrypted on the local filesystem, however this bug means that the cached files are written out to logs unencrypted.

Users are recommended to upgrade to versions 3.5.11, 3.6.6, 4.0.7 or 4.1.1, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-48795
- https://github.com/apache/cxf/pull/2258
- https://github.com/apache/cxf/commit/1c1d687f8e295f433a3592a3bc0b0a63c432bfde
- https://github.com/apache/cxf
- https://lists.apache.org/thread/vo5qv02mvv5plmb6z2xf1ktjmrpv3jmn
- http://www.openwall.com/lists/oss-security/2025/07/15/3
