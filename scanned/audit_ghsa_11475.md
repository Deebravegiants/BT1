# [H] Plane is Vulnerable to Unauthenticated Workspace Member Information Disclosure

## Summary
Severity: High
Advisory: GHSA-87x4-j8vh-p5qf
CVE: CVE-2026-30244
CWE: CWE-200, CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-87x4-j8vh-p5qf
Type: github-advisory

## Affected
- PyPI: `plane` — affected >=0

## Details
## Executive Summary

A security vulnerability exists in the Plane project management platform that allows unauthenticated attackers to enumerate workspace members and extract sensitive information including email addresses, user roles, and internal identifiers. The vulnerability stems from Django REST Framework permission classes being incorrectly configured to allow anonymous access to protected endpoints.

This vulnerability enables attackers to:

- Enumerate all members of any workspace without authentication
- Extract user email addresses and personally identifiable information (PII)
- Identify administrative accounts for targeted attacks
- Map organizational structure and user roles
- Conduct reconnaissance for social engineering attacks


**Affected Endpoints:**

```
GET /api/public/workspaces/{workspace_slug}/members/
GET /api/public/workspaces/{workspace_slug}/projects/{project_id}/members/
```
A fix is available at https://github.com/makeplane/plane/releases/tag/v1.2.3.

## References
- https://github.com/makeplane/plane/security/advisories/GHSA-87x4-j8vh-p5qf
- https://nvd.nist.gov/vuln/detail/CVE-2026-30244
- https://github.com/makeplane/plane
- https://github.com/makeplane/plane/releases/tag/v1.2.2
