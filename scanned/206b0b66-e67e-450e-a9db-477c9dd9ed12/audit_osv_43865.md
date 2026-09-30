# [M] OpenViking Debug Vector Endpoints Multi-tenant Data Exposure

## Summary
Severity: Medium
Advisory: CVE-2026-75480
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-75480
Type: osv

## Details
OpenViking debug vector scroll and count endpoints apply only account-level scoping without user-level access controls, allowing authenticated users to read all co-tenant records. Attackers can query these endpoints to retrieve private memories, resources, skills, and secret material belonging to other users in the same account without administrative privileges.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75480.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75480
- https://www.vulncheck.com/advisories/openviking-debug-vector-endpoints-multi-tenant-data-exposure
- https://github.com/volcengine/OpenViking/issues/3724
- https://github.com/volcengine/OpenViking
- https://github.com/volcengine/OpenViking/blob/main/openviking/storage/viking_vector_index_backend.py
