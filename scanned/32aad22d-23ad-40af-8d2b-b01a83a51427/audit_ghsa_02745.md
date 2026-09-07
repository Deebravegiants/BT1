# [H] Improper Restriction of Excessive Authentication Attempts in Argo API

## Summary
Severity: High
Advisory: GHSA-xcqr-9h24-vrgw
CVE: CVE-2020-8827
CWE: CWE-307
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-07-26
Source: https://github.com/advisories/GHSA-xcqr-9h24-vrgw
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd` — affected >=0 <1.5.1

## Details
As of v1.5.0, the Argo API does not implement anti-automation measures such as rate limiting, account lockouts, or other anti-bruteforce measures. Attackers can submit an unlimited number of authentication attempts without consequence.

### Specific Go Packages Affected
github.com/argoproj/argo-cd/util/cache

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8827
- https://github.com/argoproj/argo-cd/pull/3369
- https://github.com/argoproj/argo-cd/pull/3404
- https://github.com/argoproj/argo-cd/commit/35a7350b7444bcaf53ee0bb11b9d8e3ae4b717a1
- https://argoproj.github.io/argo-cd/operator-manual/user-management/#disable-admin-user
- https://argoproj.github.io/argo-cd/security_considerations
- https://github.com/argoproj/argo/releases
- https://www.soluble.ai/blog/argo-cves-2020
