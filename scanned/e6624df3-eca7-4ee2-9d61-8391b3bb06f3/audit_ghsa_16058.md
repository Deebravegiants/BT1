# [H] Harbor fails to validate the user permissions when updating p2p preheat policies

## Summary
Severity: High
Advisory: GHSA-r864-28pw-8682
CVE: CVE-2022-31668
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-11-14
Source: https://github.com/advisories/GHSA-r864-28pw-8682
Type: github-advisory

## Affected
- Go: `github.com/goharbor/harbor` — affected >=2.0.0 <2.4.3
- Go: `github.com/goharbor/harbor` — affected >=2.5.0 <2.5.2
- Go: `github.com/goharbor/harbor/src` — affected >=0 <0.0.0-20220630175814-b4ef1db

## Details
Harbor fails to validate the user permissions when updating p2p preheat policies. By sending a request to update a p2p preheat policy with an id that belongs to a project that the currently authenticated user doesn't have access to, the attacker could modify p2p preheat policies configured in other projects.

## References
- https://github.com/goharbor/harbor/security/advisories/GHSA-3wpx-625q-22j7
- https://nvd.nist.gov/vuln/detail/CVE-2022-31668
- https://github.com/goharbor/harbor
- https://pkg.go.dev/vuln/GO-2024-3268
