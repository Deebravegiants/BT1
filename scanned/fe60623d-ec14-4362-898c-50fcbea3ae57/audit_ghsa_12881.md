# [H] Gravitee API Management contains Path Traversal

## Summary
Severity: High
Advisory: GHSA-vp62-m958-qj8c
CVE: CVE-2022-38723
CWE: CWE-22, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-04
Source: https://github.com/advisories/GHSA-vp62-m958-qj8c
Type: github-advisory

## Affected
- Maven: `io.gravitee.apim:gravitee-api-management` — affected >=0 <3.15.13

## Details
**This CVE addresses the partial fix for CVE-2019-25075**

Gravitee API Management before 3.15.13 allows path traversal through HTML injection. A certain HTML injection combined with path traversal in the Email service in Gravitee API Management before 3.15.13 allows anonymous users to read arbitrary files via a /management/users/register request.

A patch was published in 2019 for this vulnerability but did not appear to have solved the issue. Version 3.15.13 did remove the flaw.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38723
- https://community.gravitee.io/t/whats-new-in-access-management-3-15-lts/164
- https://gist.github.com/garatc/d86cdb1fa2e35a7ee719d9a0de0b5ca3
- https://github.com/advisories/GHSA-xc4w-28g8-vqm5
- https://github.com/gravitee-io/gravitee-api-management
