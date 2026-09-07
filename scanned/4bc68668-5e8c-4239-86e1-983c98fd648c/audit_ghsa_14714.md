# [M] Boundary Community Edition Incorrectly Handles HTTP Requests On Initialization Which May Lead to a Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-xx83-cxmq-x89m
CVE: CVE-2024-12289
CWE: CWE-460, CWE-665
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-12-13
Source: https://github.com/advisories/GHSA-xx83-cxmq-x89m
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/boundary` — affected >=0 <0.18.2

## Details
Boundary Community Edition and Boundary Enterprise (“Boundary”) incorrectly handle HTTP requests during the initialization of the Boundary controller, which may cause the Boundary server to terminate prematurely. Boundary is only vulnerable to this flaw during the initialization of the Boundary controller, which on average is measured in milliseconds during the Boundary startup process.

This vulnerability, CVE-2024-12289, is fixed in Boundary Community Edition and Boundary Enterprise 0.16.4, 0.17.3, 0.18.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-12289
- https://discuss.hashicorp.com/t/hcsec-2024-28-boundary-controller-incorrectly-handles-http-requests-on-initialization-which-may-lead-to-a-denial-of-service
- https://github.com/hashicorp/boundary
