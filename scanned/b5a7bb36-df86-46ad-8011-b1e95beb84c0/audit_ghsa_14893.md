# [M] Unauthenticated Access to sensitive settings in Argo CD

## Summary
Severity: Medium
Advisory: GHSA-87p9-x75h-p4j2
CVE: CVE-2024-37152
CWE: CWE-22, CWE-287, CWE-306, CWE-384
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-06-06
Source: https://github.com/advisories/GHSA-87p9-x75h-p4j2
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd/v2/server` — affected >=2.9.3 <2.9.17
- Go: `github.com/argoproj/argo-cd/v2/server` — affected >=2.10.0 <2.10.12
- Go: `github.com/argoproj/argo-cd/v2/server` — affected >=2.11.0 <2.11.3

## Details
# Summary
The CVE allows unauthorized access to the sensitive settings exposed by  /api/v1/settings endpoint without authentication. 

# Details
## **Unauthenticated Access:**

### Endpoint: /api/v1/settings
Description: This endpoint is accessible without any form of authentication as expected. All sensitive settings are hidden except `passwordPattern`. 

Patches
A patch for this vulnerability has been released in the following Argo CD versions:

v2.11.3
v2.10.12
v2.9.17


# Impact
## Unauthenticated Access:

* Type: Unauthorized Information Disclosure.
* Affected Parties: All users and administrators of the Argo CD instance.
* Potential Risks: Exposure of sensitive configuration data, including but not limited to deployment settings, security configurations, and internal network information.

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-87p9-x75h-p4j2
- https://nvd.nist.gov/vuln/detail/CVE-2024-37152
- https://github.com/argoproj/argo-cd/commit/256d90178b11b04bc8174d08d7b663a2a7b1771b
- https://github.com/argoproj/argo-cd
- https://pkg.go.dev/vuln/GO-2024-2902
