# [C] xxl-rpc deserialization vulnerability

## Summary
Severity: Critical
Advisory: GHSA-c29g-q3h3-mwcf
CVE: CVE-2023-33496
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-07
Source: https://github.com/advisories/GHSA-c29g-q3h3-mwcf
Type: github-advisory

## Affected
- Maven: `com.xuxueli:xxl-rpc-core` — affected >=0

## Details
xxl-rpc v1.7.0 was discovered to contain a deserialization vulnerability via the component `com.xxl.rpc.core.remoting.net.impl.netty.codec.NettyDecode#decode`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33496
- https://github.com/edirc-wong/record/blob/main/deserialization_vulnerability_report.md
- https://github.com/xuxueli/xxl-rpc
