# [M] Unauthorized ShadowAttribute modification in MISP via client-supplied identifier

## Summary
Severity: Medium
Advisory: CVE-2026-9136
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-9136
Type: osv

## Details
A vulnerability was identified in the ShadowAttribute proposal creation workflow. The add action accepted user-controlled ShadowAttribute request data without removing the id field before saving the record. Because the underlying framework treats a supplied primary key as an instruction to update an existing record, an authenticated user able to submit shadow attribute proposals could provide the identifier of an existing ShadowAttribute and cause that record to be updated instead of creating a new proposal.




This can result in unauthorized modification of existing shadow attributes, potentially affecting proposals associated with events the user should not be able to alter. Depending on deployment configuration and accessible API responses, the issue may also expose or move proposal data across event contexts.




The vulnerability is caused by trusting a client-supplied primary key during object creation. The fix removes the id field from incoming ShadowAttribute data before processing, ensuring that the endpoint always creates a new proposal rather than updating an existing one. This has been fixed in MISP 2.5.38.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9136.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-9136
- https://github.com/MISP/MISP/commit/49911b1d4b6e4517d803e50e3d980aaa4d37c16d
