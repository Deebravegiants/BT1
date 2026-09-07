# [H] Grafana Cross-Site-Scripting (XSS) via custom loaded frontend plugin

## Summary
Severity: High
Advisory: GHSA-q53q-gxq9-mgrj
CVE: CVE-2025-4123
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2025-05-22
Source: https://github.com/advisories/GHSA-q53q-gxq9-mgrj
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=0 <0.0.0-20250521183405-c7a690348df7

## Details
A cross-site scripting (XSS) vulnerability exists in Grafana caused by combining a client path traversal and open redirect. This allows attackers to redirect users to a website that hosts a frontend plugin that will execute arbitrary JavaScript. This vulnerability does not require editor permissions and if anonymous access is enabled, the XSS will work. If the Grafana Image Renderer plugin is installed, it is possible to exploit the open redirect to achieve a full read SSRF.

The default Content-Security-Policy (CSP) in Grafana will block the XSS though the `connect-src` directive.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-4123
- https://github.com/grafana/grafana/commit/c7a690348df761d41b659224cbc50a46a0c0e4cc
- https://github.com/grafana/grafana
- https://grafana.com/blog/2025/05/23/grafana-security-release-medium-and-high-severity-security-fixes-for-cve-2025-4123-and-cve-2025-3580
- https://grafana.com/security/security-advisories/cve-2025-4123
- https://pkg.go.dev/vuln/GO-2025-3702
- https://www.exploit-db.com/exploits/52491
