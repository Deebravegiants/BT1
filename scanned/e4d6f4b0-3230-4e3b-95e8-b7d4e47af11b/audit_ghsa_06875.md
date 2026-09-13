# [H] Apache HttpComponents Core HTTP/1 header parsing can cause memory-exhaustion denial of service

## Summary
Severity: High
Advisory: GHSA-hf6x-8p5f-cgmf
CVE: CVE-2026-54399
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-hf6x-8p5f-cgmf
Type: github-advisory

## Affected
- Maven: `org.apache.httpcomponents.core5:httpcore5` — affected >=0 <5.4.3
- Maven: `org.apache.httpcomponents.core5:httpcore5` — affected >=5.5-alpha1 <5.5-beta2

## Details
Uncontrolled Resource Consumption vulnerability in the HTTP/1.1 message parser in Apache HttpComponents Core (5.4.2 and earlier, 5.5-beta1 and earlier) allows a remote attacker to cause a denial of service through memory exhaustion by sending messages with excessive number of headers / excessive header length

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-54399
- https://github.com/apache/httpcomponents-core/commit/d96a00fec9b2e19f8005e35681df5f6cd6e21a9e
- https://github.com/apache/httpcomponents-core/commit/fdc53a32fe0fccf098cc67e71cd125e447c759ed
- https://github.com/apache/httpcomponents-core
- https://lists.apache.org/thread/zmxh1pl2zohov5ntdh4lt85gfrlchgpy
- http://www.openwall.com/lists/oss-security/2026/07/01/4
