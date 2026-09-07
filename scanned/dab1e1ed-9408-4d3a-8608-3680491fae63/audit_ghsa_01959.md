# [M] Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-cpgw-2wxr-pww3
CVE: CVE-2018-15178
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-29
Source: https://github.com/advisories/GHSA-cpgw-2wxr-pww3
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.12.0

## Details
Open redirect vulnerability in Gogs before 0.12 allows remote attackers to redirect users to arbitrary websites and conduct phishing attacks via an initial /\ substring in the user/login redirect_to parameter, related to the function isValidRedirect in routes/user/auth.go.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-15178
- https://github.com/gogs/gogs/issues/5364
- https://github.com/gogs/gogs/pull/5365
- https://github.com/gogs/gogs/commit/1f247cf8139cb483276cd8dd06385a800ce9d4b2
