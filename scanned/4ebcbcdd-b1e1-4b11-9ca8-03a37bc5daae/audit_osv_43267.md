# [M] stoatchat before 0.15.0 Uncapped SVG Rendering Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-73057
Aliases: GHSA-x87r-h3mq-7mgr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-16
Source: https://osv.dev/vulnerability/CVE-2026-73057
Type: osv

## Details
stoatchat before 0.15.0 fails to validate SVG viewBox dimensions in the proxy endpoint, allowing attackers to cause denial of service by memory exhaustion. Attackers can host malicious SVGs with extremely large width and height values and trigger concurrent requests to exhaust available memory across proxy replicas.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73057.json
- https://github.com/stoatchat/stoatchat/security/advisories/GHSA-x87r-h3mq-7mgr
- https://nvd.nist.gov/vuln/detail/CVE-2026-73057
- https://www.vulncheck.com/advisories/stoatchat-before-uncapped-svg-rendering-denial-of-service
