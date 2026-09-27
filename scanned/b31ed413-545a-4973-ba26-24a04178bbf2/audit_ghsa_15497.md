# [H] ZITADEL Allows Unauthorized Access After Organization or Project Deactivation

## Summary
Severity: High
Advisory: GHSA-jj94-6f5c-65r8
CVE: CVE-2024-47060
CWE: CWE-200, CWE-672
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-09-19
Source: https://github.com/advisories/GHSA-jj94-6f5c-65r8
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.62.0 <2.62.1
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.61.0 <2.61.1
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.60.0 <2.60.2
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.59.0 <2.59.3
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.58.0 <2.58.5
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.57.0 <2.57.5
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.56.0 <2.56.6
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.55.0 <2.55.8
- Go: `github.com/zitadel/zitadel/v2` — affected >=0 <2.54.10

## Details
### Summary
In Zitadel, even after an organization is deactivated, associated projects, respectively their applications remain active. Users across other organizations can still log in and access through these applications, leading to unauthorized access.
Additionally, if a project was deactivated access to applications was also still possible.

### Details
The issue stems from the fact that when an organization is deactivated in Zitadel, the applications associated with it do not automatically deactivate. The application lifecycle is not tightly coupled with the organization's lifecycle, leading to a situation where the organization or project is marked as inactive, but its resources remain accessible.

### PoC
- Create a new Organization, create new project and setup OpenID connect.
- Deactivate an Organization
- Setup authentication without selecting Check for Project on Authentication
- User is able to login despite the organization is deactivated

### Impact
This vulnerability allows for unauthorized access to projects and their resources, which should have been restricted post-organization deactivation.

### Patches

2.x versions are fixed on >= [2.62.1](https://github.com/zitadel/zitadel/releases/tag/v2.62.1)
2.61.x versions are fixed on >= [2.61.1](https://github.com/zitadel/zitadel/releases/tag/v2.61.1)
2.60.x versions are fixed on >= [2.60.2](https://github.com/zitadel/zitadel/releases/tag/v2.60.2)
2.59.x versions are fixed on >= [2.59.3](https://github.com/zitadel/zitadel/releases/tag/v2.59.3)
2.58.x versions are fixed on >= [2.58.5](https://github.com/zitadel/zitadel/releases/tag/v2.58.5)
2.57.x versions are fixed on >= [2.57.5](https://github.com/zitadel/zitadel/releases/tag/v2.57.5)
2.56.x versions are fixed on >= [2.56.6](https://github.com/zitadel/zitadel/releases/tag/v2.56.6)
2.55.x versions are fixed on >= [2.55.8](https://github.com/zitadel/zitadel/releases/tag/v2.55.8)
2.54.x versions are fixed on >= [2.54.10](https://github.com/zitadel/zitadel/releases/tag/v2.54.10)

### Workaround
Unpatched versions can explicitly disable the application to make sure the client is not allowed anymore.

### Questions
If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

### Credits
Thanks to @prdp1137 for reporting this!

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-jj94-6f5c-65r8
- https://nvd.nist.gov/vuln/detail/CVE-2024-47060
- https://github.com/zitadel/zitadel
