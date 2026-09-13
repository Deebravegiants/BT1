# [H] Skupper uses a static cookie secret for the openshift oauth-proxy

## Summary
Severity: High
Advisory: GHSA-w799-v85j-88pg
CVE: CVE-2024-6535
CWE: CWE-1392, CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-17
Source: https://github.com/advisories/GHSA-w799-v85j-88pg
Type: github-advisory

## Affected
- Go: `github.com/skupperproject/skupper` — affected >=0 <0.0.0-20240703184342-c26bce4079ff

## Details
A flaw was found in Skupper. When Skupper is initialized with the console-enabled and with console-auth set to Openshift, it configures the openshift oauth-proxy with a static cookie-secret. In certain circumstances, this may allow an attacker to bypass authentication to the Skupper console via a specially-crafted cookie.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6535
- https://github.com/skupperproject/skupper/commit/d2cb3782e807853694ee66b6e3d4a1917485eb71
- https://access.redhat.com/errata/RHSA-2024:4865
- https://access.redhat.com/errata/RHSA-2024:4871
- https://access.redhat.com/security/cve/CVE-2024-6535
- https://bugzilla.redhat.com/show_bug.cgi?id=2296024
- https://github.com/skupperproject/skupper
