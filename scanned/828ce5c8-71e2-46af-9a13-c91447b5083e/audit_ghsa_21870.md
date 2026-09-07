# [M] Authorization bypass in Istio

## Summary
Severity: Medium
Advisory: GHSA-82mm-ffjr-h86c
CVE: CVE-2020-16844
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-82mm-ffjr-h86c
Type: github-advisory

## Affected
- Go: `istio.io/istio` — affected >=1.5.0 <1.5.9
- Go: `istio.io/istio` — affected >=1.6.0 <1.6.8

## Details
In Istio 1.5.0 though 1.5.8 and Istio 1.6.0 through 1.6.7, when users specify an AuthorizationPolicy resource with DENY actions using wildcard suffixes (e.g. *-some-suffix) for source principals or namespace fields, callers will never be denied access, bypassing the intended policy.

### Specific Go Packages Affected
istio.io/istio/pilot/pkg/security/authz/model/matcher

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-16844
- https://github.com/istio/istio/commit/4c73414556b83f0e75c1b3a0a89a23103a71573c
- https://github.com/istio/istio/commit/72d2e135374f421b656d6f1a21f474db46134ace
- https://github.com/istio/istio/releases
- https://github.com/istio/istio/releases/tag/1.5.9
- https://github.com/istio/istio/releases/tag/1.6.8
- https://istio.io/latest/news/releases/1.5.x/announcing-1.5.9
- https://istio.io/latest/news/releases/1.6.x/announcing-1.6.8
- https://istio.io/latest/news/security/istio-security-2020-009
