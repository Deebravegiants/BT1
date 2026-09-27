# [H] CVE-2024-45969

## Summary
Severity: High
Advisory: CVE-2024-45969
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-15
Source: https://osv.dev/vulnerability/CVE-2024-45969
Type: osv

## Details
NULL pointer dereference in the MMS Client in MZ Automation LibIEC1850 before commit 7afa40390b26ad1f4cf93deaa0052fe7e357ef33 allows a malicious server to Cause a Denial-of-Service via the MMS InitiationResponse message.

## References
- https://encs.eu/news/critical-security-vulnerabilities-discovered-in-mz-automations-mms-client/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45969.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45969
- https://github.com/mz-automation/libiec61850/commit/7afa40390b26ad1f4cf93deaa0052fe7e357ef33
