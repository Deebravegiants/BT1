# [M] github.com/gitpod-io/gitpod vulnerable to Cookie Tossing

## Summary
Severity: Medium
Advisory: GHSA-8pgc-65mj-53h5
CVE: CVE-2024-21583
CWE: CWE-15, CWE-565
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-07-19
Source: https://github.com/advisories/GHSA-8pgc-65mj-53h5
Type: github-advisory

## Affected
- Go: `github.com/gitpod-io/gitpod` — affected >=0

## Details
Versions of the package github.com/gitpod-io/gitpod/components/server/go/pkg/lib before main-gha.27122; versions of the package github.com/gitpod-io/gitpod/components/ws-proxy/pkg/proxy before main-gha.27122; versions of the package github.com/gitpod-io/gitpod/install/installer/pkg/components/auth before main-gha.27122; versions of the package github.com/gitpod-io/gitpod/install/installer/pkg/components/public-api-server before main-gha.27122; versions of the package github.com/gitpod-io/gitpod/install/installer/pkg/components/server before main-gha.27122; versions of the package @gitpod/gitpod-protocol before 0.1.5-main-gha.27122 are vulnerable to Cookie Tossing due to a missing __Host- prefix on the _gitpod_io_jwt2_ session cookie. This allows an adversary who controls a subdomain to set the value of the cookie on the Gitpod control plane, which can be assigned to an attacker’s own JWT so that specific actions taken by the victim (such as connecting a new Github organization) are actioned by the attackers session.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21583
- https://github.com/gitpod-io/gitpod/pull/19973
- https://github.com/gitpod-io/gitpod/commit/da1053e1013f27a56e6d3533aa251dbd241d0155
- https://app.safebase.io/portal/71ccd717-aa2d-4a1e-942e-c768d37e9e0c/preview?product=%5B%E2%80%A6%5D942e-c768d37e9e0c&tcuUid=1d505bda-9a38-4ca5-8724-052e6337f34d
- https://github.com/gitpod-io/gitpod
- https://pkg.go.dev/vuln/GO-2024-2997
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGITPODIOGITPODCOMPONENTSSERVERGOPKGLIB-7452074
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGITPODIOGITPODCOMPONENTSWSPROXYPKGPROXY-7452075
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGITPODIOGITPODINSTALLINSTALLERPKGCOMPONENTSAUTH-7452076
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGITPODIOGITPODINSTALLINSTALLERPKGCOMPONENTSPUBLICAPISERVER-7452077
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGITPODIOGITPODINSTALLINSTALLERPKGCOMPONENTSSERVER-7452078
- https://security.snyk.io/vuln/SNYK-JS-GITPODGITPODPROTOCOL-7452079
