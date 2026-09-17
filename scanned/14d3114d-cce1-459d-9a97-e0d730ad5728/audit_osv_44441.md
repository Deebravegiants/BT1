# [M] Chainlit Feedback Endpoints Missing Ownership Validation

## Summary
Severity: Medium
Advisory: CVE-2026-82290
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82290
Type: osv

## Details
Chainlit through 2.12.0 fails to validate ownership of feedback records in PUT and DELETE endpoints. Authenticated attackers can delete or modify other users' feedback by supplying arbitrary feedback identifiers, corrupting human-rating data used for model evaluation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82290.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82290
- https://www.vulncheck.com/advisories/chainlit-feedback-endpoints-missing-ownership-validation
- https://github.com/Chainlit/chainlit/issues/2975
- https://github.com/Chainlit/chainlit
- https://github.com/Chainlit/chainlit/blob/190ea74239d9e84b26e7c91bc2882dd038942564/backend/chainlit/server.py
