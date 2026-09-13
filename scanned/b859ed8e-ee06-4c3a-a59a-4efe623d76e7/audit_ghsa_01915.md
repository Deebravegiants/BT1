# [M] Kiali Authentication Bypass vulnerability

## Summary
Severity: Medium
Advisory: GHSA-ggjr-2f7v-vhq4
CVE: CVE-2021-20278
CWE: CWE-287, CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-01
Source: https://github.com/advisories/GHSA-ggjr-2f7v-vhq4
Type: github-advisory

## Affected
- Go: `github.com/kiali/kiali` — affected >=0 <1.31.0

## Details
An authentication bypass vulnerability was found in Kiali in versions before 1.31.0 when the authentication strategy `OpenID` is used. When RBAC is enabled, Kiali assumes that some of the token validation is handled by the underlying cluster. When OpenID `implicit flow` is used with RBAC turned off, this token validation doesn't occur, and this allows a malicious user to bypass the authentication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20278
- https://bugzilla.redhat.com/show_bug.cgi?id=1937171
- https://kiali.io/news/security-bulletins/kiali-security-002
