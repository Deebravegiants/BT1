# [M] Open Redirect in github.com/AndrewBurian/powermux

## Summary
Severity: Medium
Advisory: GHSA-mj9r-wwm8-7q52
CVE: CVE-2021-32721
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-07-01
Source: https://github.com/advisories/GHSA-mj9r-wwm8-7q52
Type: github-advisory

## Affected
- Go: `github.com/AndrewBurian/powermux` — affected >=0 <1.1.1

## Details
### Impact
Attackers may be able to craft phishing links and other open redirects by exploiting the trailing slash redirection feature. This may lead to users being redirected to untrusted sites after following an attacker crafted link.

### Patches
The issue is resolved in v1.1.1

### Workarounds
There are no existing workarounds.
You may detect attempts to craft urls that exploit this feature by looking for request paths containing pairs of forward slashes in sequence combined with a trailing slash e.g. `https://example.com//foo/`

## References
- https://github.com/AndrewBurian/powermux/security/advisories/GHSA-mj9r-wwm8-7q52
- https://nvd.nist.gov/vuln/detail/CVE-2021-32721
- https://github.com/AndrewBurian/powermux/pull/42
- https://github.com/AndrewBurian/powermux/commit/5e60a8a0372b35a898796c2697c40e8daabed8e9
