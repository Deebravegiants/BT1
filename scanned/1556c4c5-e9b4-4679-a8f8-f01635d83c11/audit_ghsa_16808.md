# [M] CA17 TeamsACS Cross Site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hwvw-gh23-qpvq
CVE: CVE-2024-22780
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-04-02
Source: https://github.com/advisories/GHSA-hwvw-gh23-qpvq
Type: github-advisory

## Affected
- Go: `github.com/ca17/teamsacs` — affected >=0

## Details
Cross Site Scripting vulnerability in CA17 TeamsACS v.1.0.1 allows a remote attacker to execute arbitrary code via a crafted script to the errmsg parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22780
- https://github.com/CA17/TeamsACS/issues/26
- https://fuo.fi/CVE-2024-22780
- https://github.com/CA17/TeamsACS
- http://ca17.com
