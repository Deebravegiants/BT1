# [C] Argo CD's Project API Token Exposes Repository Credentials

## Summary
Severity: Critical
Advisory: GHSA-786q-9hcg-v9ff
CVE: CVE-2025-55190
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-04
Source: https://github.com/advisories/GHSA-786q-9hcg-v9ff
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.13.0 <2.13.9
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.14.0 <2.14.16
- Go: `github.com/argoproj/argo-cd/v3` — affected >=0 <3.0.14
- Go: `github.com/argoproj/argo-cd/v3` — affected >=3.1.0-rc1 <3.1.2

## Details
### Summary
Argo CD API tokens with project-level permissions are able to retrieve sensitive repository credentials (usernames, passwords) through the project details API endpoint, even when the token only has standard application management permissions and no explicit access to secrets.

Component: `Project API (/api/v1/projects/{project}/detailed)`


## Vulnerability Details
### Expected Behavior
API tokens should require explicit permission to access sensitive credential information. Standard project permissions should not grant access to repository secrets.
### Actual Behavior
API tokens with basic project permissions can retrieve all repository credentials associated with a project through the detailed project API endpoint.

**Note**: This vulnerability does not only affect project-level permissions. Any token with project get permissions is also vulnerable, including global permissions such as: `p, role/user, projects, get, *, allow`

### Steps to Reproduce

1. Create an API token with the following project-level permissions:
  ```
  p, proj:myProject:project-automation-role, applications, sync, myProject/*, allow
  p, proj:myProject:project-automation-role, applications, action/argoproj.io/Rollout/*, myProject/*, allow
  p, proj:myProject:project-automation-role, applications, get, myProject/*, allow
  ```

2. Call the project details API:
  ```
  bashcurl -sH "Authorization: Bearer $ARGOCD_API_TOKEN" \
    "https://argocd.example.com/api/v1/projects/myProject/detailed"
  
  ```
3. Observe that the response includes sensitive repository credentials:
  ```
  {
    "repositories": [
      {
        "username": "<REDACTED>",
        "password": "<REDACTED>",
        "type": "helm",
        "name": "test-helm-repo",
        "project": "myProject"
      }
    ]
  }
  ```

## Patches

* v3.1.2
* v3.0.14
* v2.14.16
* v2.13.9


Credits to @ashishgoyal111 for helping identify this issue.

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-786q-9hcg-v9ff
- https://nvd.nist.gov/vuln/detail/CVE-2025-55190
- https://github.com/argoproj/argo-cd/commit/e8f86101f5378662ae6151ce5c3a76e9141900e8
- https://github.com/argoproj/argo-cd
