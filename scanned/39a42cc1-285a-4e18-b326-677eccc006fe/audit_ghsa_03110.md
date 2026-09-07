# [H] Cross-site Request Forgery (CSRF) in Cloud Native Computing Foundation Harbor

## Summary
Severity: High
Advisory: GHSA-rffr-c932-cpxv
CVE: CVE-2019-19025
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-rffr-c932-cpxv
Type: github-advisory

## Affected
- Go: `github.com/goharbor/harbor` — affected >=1.7.0 <1.8.6
- Go: `github.com/goharbor/harbor` — affected >=1.9.0 <1.9.3

## Details
Cure53 has discovered that the Harbor web interface does not implement protection mechanisms against Cross-Site Request Forgery (CSRF). By luring an authenticated user onto a prepared third-party website, an attacker can execute any action on the platform in the context of the currently authenticated victim.

The vulnerability was immediately fixed by the Harbor team and all supported versions were patched.

Successful exploitation of this issue will lead to 3rd parties executing actions on the platform of behalf of authenticated users and administrators.

If your product uses the affected releases of Harbor, update to version 1.8.6 and 1.9.3 to patch this issue immediately.

https://github.com/goharbor/harbor/releases/tag/v1.8.6
https://github.com/goharbor/harbor/releases/tag/v1.9.3

## References
- https://github.com/goharbor/harbor/security/advisories/GHSA-gcqm-v682-ccw6
- https://nvd.nist.gov/vuln/detail/CVE-2019-19025
- https://github.com/goharbor/harbor/security/advisories
- https://tanzu.vmware.com/security/cve-2019-19025
