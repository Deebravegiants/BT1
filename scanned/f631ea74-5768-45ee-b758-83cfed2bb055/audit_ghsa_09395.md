# [C] Casdoor has an authentication bypass

## Summary
Severity: Critical
Advisory: GHSA-fwgq-j9r9-qjgr
CVE: CVE-2026-9090
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-fwgq-j9r9-qjgr
Type: github-advisory

## Affected
- Go: `github.com/casdoor/casdoor` — affected >=0

## Details
Casdoor versions 2.362.0 and earlier contain a vulnerability that allows an attacker to bypass authentication by supplying an arbitrary signing certificate. The buildSpCertificateStore function extracts the X.509 certificate directly from the incoming SAMLResponse instead of using the trusted pre-configured Identity Provider certificate, allowing an attacker to forge assertions signed with an attacker-controlled key.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9090
- https://github.com/casdoor/casdoor
- https://kb.cert.org/vuls/id/780781
