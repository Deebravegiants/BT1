# [C] HestiaCP 1.9.0-1.9.4 Deserialization RCE via Web Terminal

## Summary
Severity: Critical
Advisory: CVE-2026-43633
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-43633
Type: osv

## Details
HestiaCP versions 1.9.0 through 1.9.4 contain a deserialization vulnerability in the web terminal component caused by a session format mismatch between PHP and Node.js that allows unauthenticated remote attackers to achieve root-level code execution. Attackers can inject crafted data into HTTP headers that are processed by the PHP session handler but incorrectly deserialized by the Node.js web terminal component as trusted session values, resulting in arbitrary command execution on systems with the web terminal feature enabled.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43633.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43633
- https://www.vulncheck.com/advisories/hestiacp-deserialization-rce-via-web-terminal
- https://github.com/hestiacp/hestiacp/issues/5229
- https://github.com/hestiacp/hestiacp/pull/5244
- https://github.com/hestiacp/hestiacp/commit/854d71b3c1737b0a0d0cc55c926008ffe1f6719b
- https://github.com/hestiacp/hestiacp
- https://mercuryiss.com.au/hestiacp-unauthenticated-rce-ip-spoofing-cve-2026-43633-cve-2026-43634
