# [M] Grafana XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-x5fh-fvvr-892f
CVE: CVE-2018-1000816
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-x5fh-fvvr-892f
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=0 <5.3.2

## Details
Grafana version confirmed for 5.2.4 and 5.3.0 contains a Cross Site Scripting (XSS) vulnerability in Influxdb and Graphite query editor that can result in Running arbitrary js code in victims browser.. This attack appear to be exploitable via Authenticated user must click on the input field where the payload was previously inserted..

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000816
- https://github.com/grafana/grafana/issues/13667
- https://github.com/grafana/grafana/pull/13670
- https://github.com/grafana/grafana/commit/eabb04cec21dc323347da1aab7fcbf2a6e9dd121
- https://github.com/grafana/grafana
