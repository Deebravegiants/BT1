# [H] CVE-2023-35953

## Summary
Severity: High
Advisory: CVE-2023-35953
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-28
Source: https://osv.dev/vulnerability/CVE-2023-35953
Type: osv

## Details
Multiple stack-based buffer overflow vulnerabilities exist in the readOFF.cpp functionality of libigl v2.4.0. A specially-crafted .off file can lead to a buffer overflow. An attacker can arbitrary code execution to trigger these vulnerabilities.This vulnerability exists within the code responsible for parsing comments within the geometric vertices section within an OFF file.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1784
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1784
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/35xxx/CVE-2023-35953.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-35953
