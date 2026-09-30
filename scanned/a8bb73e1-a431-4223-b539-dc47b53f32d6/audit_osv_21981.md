# [H] CVE-2022-21159

## Summary
Severity: High
Advisory: CVE-2022-21159
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-15
Source: https://osv.dev/vulnerability/CVE-2022-21159
Type: osv

## Details
A denial of service vulnerability exists in the parseNormalModeParameters functionality of MZ Automation GmbH libiec61850 1.5.0. A specially-crafted series of network requests can lead to denial of service. An attacker can send a sequence of malformed iec61850 messages to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1467
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2022-1467
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21159.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-21159
- https://github.com/mz-automation/libiec61850/commit/cfa94cbf10302bedc779703f874ee2e8387a0721
