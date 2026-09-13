# [M] changedetection.io - Missing Authentication on /api/v1/full-spec Discloses Full OpenAPI Schema

## Summary
Severity: Medium
Advisory: CVE-2026-71203
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71203
Type: osv

## Details
changedetection.io's REST API resources are protected by an @auth.check_token decorator validating the caller's x-api-key header, except the Spec resource registered at /api/v1/full-spec (changedetectionio/api/Spec.py), whose get method carries neither @auth.check_token nor @validate_openapi_request.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71203.json
- https://github.com/dgtlmoon/changedetection.io
- https://nvd.nist.gov/vuln/detail/CVE-2026-71203
