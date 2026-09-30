# [H] Partial Account Takeover due to Insecure Data Querying in infiniflow/ragflow

## Summary
Severity: High
Advisory: CVE-2024-12880
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12880
Type: osv

## Details
A vulnerability in infiniflow/ragflow version RAGFlow-0.13.0 allows for partial account takeover via insecure data querying. The issue arises from the way tenant IDs are handled in the application. If a user has access to multiple tenants, they can manipulate their tenant access to query and access API tokens of other tenants. This vulnerability affects the following endpoints: /v1/system/token_list, /v1/system/new_token, /v1/api/token_list, /v1/api/new_token, and /v1/api/rm. An attacker can exploit this to access other tenants' API tokens, perform actions on behalf of other tenants, and access their data.

## References
- https://huntr.com/bounties/c41c7eaa-554a-408c-96be-9dba56113970
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12880.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12880
