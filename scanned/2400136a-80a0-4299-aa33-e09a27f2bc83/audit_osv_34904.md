# [H] CVE-2025-66384

## Summary
Severity: High
Advisory: CVE-2025-66384
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:H/A:L)
Published: 2025-11-28
Source: https://osv.dev/vulnerability/CVE-2025-66384
Type: osv

## Details
app/Controller/EventsController.php in MISP before 2.5.24 has invalid logic in checking for uploaded file validity, related to tmp_name.

## References
- https://github.com/MISP/MISP/compare/v2.5.23...v2.5.24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66384.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66384
- https://github.com/misp/misp/commit/6867f0d3157a1959154bdad9ddac009dec6a19f5
