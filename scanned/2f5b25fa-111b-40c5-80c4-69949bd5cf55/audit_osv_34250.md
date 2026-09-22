# [H] CVE-2025-56568

## Summary
Severity: High
Advisory: CVE-2025-56568
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/CVE-2025-56568
Type: osv

## Details
Assertion failure vulnerability in the PCO (Protocol Configuration Options) parser in the SMF (Session Management Function) component of Open5GS before v2.7.5 allows remote attackers to cause denial of service via specially crafted NGAP messages containing malformed length fields in protocol configuration data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/56xxx/CVE-2025-56568.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-56568
- https://github.com/open5gs/open5gs/issues/3969
- https://github.com/open5gs/open5gs/commit/d7707879c943d2c952235382154d835b5849d54e
