# [H] CVE-2021-26923

## Summary
Severity: High
Advisory: CVE-2021-26923
Aliases: GHSA-pfgj-mh5m-2p48
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-03-15
Source: https://osv.dev/vulnerability/CVE-2021-26923
Type: osv

## Details
An issue was discovered in Argo CD before 1.8.4. Accessing the endpoint /api/version leaks internal information for the system, and this endpoint is not protected with authentication.

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-pfgj-mh5m-2p48
- https://github.com/argoproj/argo-cd/compare/v1.8.3...v1.8.4
