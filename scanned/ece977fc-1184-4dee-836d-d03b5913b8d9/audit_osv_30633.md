# [H] CVE-2024-53450

## Summary
Severity: High
Advisory: CVE-2024-53450
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-12-09
Source: https://osv.dev/vulnerability/CVE-2024-53450
Type: osv

## Details
RAGFlow 0.13.0 suffers from improper access control in document-hooks.ts, allowing unauthorized access to user documents.

## References
- https://github.com/infiniflow/ragflow/blob/cec208051f6f5996fefc8f36b6b71231b1807533/web/src/hooks/document-hooks.ts#L23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53450.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53450
- https://github.com/thanhtung4102/Unauthentication-in-Ragflow
