# [H] Grafana is vulnerable to XSS attacks through open redirects and path traversal

## Summary
Severity: High
Advisory: GHSA-vqph-p5vc-g644
CVE: CVE-2025-6023
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2025-07-18
Source: https://github.com/advisories/GHSA-vqph-p5vc-g644
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=0 <1.9.2-0.20250521205822-0ba0b99665a9

## Details
An open redirect vulnerability has been identified in Grafana OSS that can be exploited to achieve XSS attacks. The vulnerability was introduced in Grafana v11.5.0.

The open redirect can be chained with path traversal vulnerabilities to achieve XSS.

Fixed in versions 12.0.2+security-01, 11.6.3+security-01, 11.5.6+security-01, 11.4.6+security-01 and 11.3.8+security-01

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6023
- https://github.com/grafana/grafana/commit/0ba0b99665a946cd96676ef85ec8bc83028cb1d7
- https://github.com/grafana/grafana/commit/40ed88fe86d347bcde5ddaed6c4a20a95d2f0d55
- https://github.com/grafana/grafana/commit/5b00e21638f565eed46acb4d0b7c009968df4c3b
- https://github.com/grafana/grafana/commit/b6dd2b70c655c61b111b328f1a7dcca6b3954936
- https://github.com/grafana/grafana/commit/e0ba4b480954f8a33aa2cff3229f6bcc05777bd9
- https://github.com/grafana/grafana
- https://grafana.com/blog/2025/07/17/grafana-security-release-medium-and-high-severity-fixes-for-cve-2025-6197-and-cve-2025-6023
- https://grafana.com/security/security-advisories/cve-2025-6023
