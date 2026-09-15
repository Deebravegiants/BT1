# [C] fastjson has a remote code execution (RCE) vulnerability

## Summary
Severity: Critical
Advisory: GHSA-crf3-v9rr-v7hj
CVE: CVE-2026-16723
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-23
Source: https://github.com/advisories/GHSA-crf3-v9rr-v7hj
Type: github-advisory

## Affected
- Maven: `com.alibaba:fastjson` — affected >=1.2.68

## Details
A remote code execution (RCE) vulnerability exists in fastjson 1.2.68 through 1.2.83. This vulnerability is exploitable under fastjson's stock default configuration — no AutoType enablement required, no classpath gadget required.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-16723
- https://github.com/alibaba/fastjson2
- https://github.com/alibaba/fastjson2/wiki/Security-Advisory:-Remote-Code-Execution-in-fastjson-1.2.68%E2%80%931.2.83
