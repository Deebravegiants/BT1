# [M] Casdoor allows users to bypass configured MFA requirements

## Summary
Severity: Medium
Advisory: GHSA-gv4m-v8c8-hr3g
CVE: CVE-2026-9091
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-gv4m-v8c8-hr3g
Type: github-advisory

## Affected
- Go: `github.com/casdoor/casdoor` — affected >=0

## Details
Casdoor versions 2.362.0 and earlier contain a logic flaw in the social‑login binding flow that allows users to bypass configured MFA requirements. The binding‑rule code path in controllers/auth.go calls HandleLoggedIn directly without invoking checkMfaEnable. Any user authenticating via this path is logged in without MFA enforcement.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9091
- https://github.com/casdoor/casdoor
- https://kb.cert.org/vuls/id/780781
