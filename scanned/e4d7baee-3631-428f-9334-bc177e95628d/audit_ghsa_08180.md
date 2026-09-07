# [M] Grafana has a Cross-site Scripting issue

## Summary
Severity: Medium
Advisory: GHSA-cqp7-wf4c-3xgc
CVE: CVE-2025-41117
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-12
Source: https://github.com/advisories/GHSA-cqp7-wf4c-3xgc
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=12.2.0 <12.2.5
- Go: `github.com/grafana/grafana` — affected >=12.3.0 <12.3.3

## Details
Stack traces in Grafana's Explore Traces view can be rendered as raw HTML, and thus inject malicious JavaScript in the browser. This would require malicious JavaScript to be entered into the stack trace field.

Only datasources with the Jaeger HTTP API appear to be affected; Jaeger gRPC and Tempo do not appear affected whatsoever.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-41117
- https://github.com/grafana/grafana/commit/4f624a5a01404da45d60063ae1ee2f184818cd42
- https://github.com/grafana/grafana/commit/8dfa6446942873d76cd94c63a2d6b71a25e880da
- https://github.com/grafana/grafana/commit/ecff0d88680cea4ad32709cb3b94b790a7f58d25
- https://github.com/grafana/grafana
- https://grafana.com/security/security-advisories/CVE-2025-41117
