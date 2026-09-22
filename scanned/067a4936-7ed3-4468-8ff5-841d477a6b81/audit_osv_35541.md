# [H] CVE-2026-10547

## Summary
Severity: High
Advisory: CVE-2026-10547
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-10547
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.10.3 does not properly validate ownership in the deprecated POST /api/v1/build/{flow_id}/vertices endpoint, allowing an authenticated user to inject arbitrary graph data into a shared cache for any flow. This may result in cross-user cache pollution, unauthorized workflow execution, or denial of service.

## References
- https://www.ibm.com/support/pages/node/7282647
