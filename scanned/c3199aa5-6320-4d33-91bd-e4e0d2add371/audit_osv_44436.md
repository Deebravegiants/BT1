# [M] BISHENG Unauthenticated Server-Side Request Forgery via Workflow Report Callback

## Summary
Severity: Medium
Advisory: CVE-2026-82285
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82285
Type: osv

## Details
bisheng through 2.6.0-fix2 contains a server-side request forgery vulnerability in the POST /api/v1/workflow/report/callback endpoint that lacks authentication and applies no URL scheme restrictions or host filtering. Unauthenticated attackers can supply arbitrary URLs to enumerate internal network services and cloud metadata endpoints, then retrieve captured responses from object storage using caller-supplied object names.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82285.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82285
- https://www.vulncheck.com/advisories/bisheng-unauthenticated-server-side-request-forgery-via-workflow-report-callback
- https://github.com/dataelement/bisheng/issues/2190
- https://github.com/dataelement/bisheng
- https://github.com/dataelement/bisheng/blob/3f27641987c7363d2d7b7b1a8c3c3dbe09c60fd7/src/backend/bisheng/api/v1/workflow.py
