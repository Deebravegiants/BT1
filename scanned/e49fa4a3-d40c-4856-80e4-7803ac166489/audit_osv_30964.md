# [H] CVE-2024-56921

## Summary
Severity: High
Advisory: CVE-2024-56921
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-03
Source: https://osv.dev/vulnerability/CVE-2024-56921
Type: osv

## Details
An issue was discovered in Open5gs v2.7.2. InitialUEMessage, Registration request sent at a specific time can crash AMF due to incorrect error handling of gmm_state_exception() function upon receipt of the Nausf_UEAuthentication_Authenticate response.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56921.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56921
- https://github.com/open5gs/open5gs/issues/3608
- https://github.com/open5gs/open5gs/commit/f780f9af45c27b6f49987d96ba71dedb3dd85840
