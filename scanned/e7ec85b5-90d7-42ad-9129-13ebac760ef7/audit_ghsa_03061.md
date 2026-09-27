# [H] Authorization bypass in github.com/dgrijalva/jwt-go

## Summary
Severity: High
Advisory: GHSA-w73w-5m7g-f7qc
CVE: CVE-2020-26160
CWE: CWE-287, CWE-755
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-w73w-5m7g-f7qc
Type: github-advisory

## Affected
- Go: `github.com/dgrijalva/jwt-go` — affected >=0.0.0-20150717181359-44718f8a89b0
- Go: `github.com/dgrijalva/jwt-go/v4` — affected >=0 <4.0.0-preview1

## Details
jwt-go allows attackers to bypass intended access restrictions in situations with `[]string{}` for `m["aud"]` (which is allowed by the specification). Because the type assertion fails, "" is the value of aud. This is a security problem if the JWT token is presented to a service that lacks its own audience check. There is no patch available and users of jwt-go are advised to migrate to [golang-jwt](https://github.com/golang-jwt/jwt) at version 3.2.1

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26160
- https://github.com/dgrijalva/jwt-go/issues/422
- https://github.com/dgrijalva/jwt-go/issues/462
- https://github.com/dgrijalva/jwt-go/pull/426
- https://github.com/dgrijalva/jwt-go/commit/ec0a89a131e3e8567adcb21254a5cd20a70ea4ab
- https://github.com/dgrijalva/jwt-go
- https://pkg.go.dev/vuln/GO-2020-0017
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMDGRIJALVAJWTGO-596515
