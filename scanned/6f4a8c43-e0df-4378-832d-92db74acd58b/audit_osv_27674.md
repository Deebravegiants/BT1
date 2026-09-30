# [H] CVE-2024-24686

## Summary
Severity: High
Advisory: CVE-2024-24686
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-28
Source: https://osv.dev/vulnerability/CVE-2024-24686
Type: osv

## Details
Multiple stack-based buffer overflow vulnerabilities exist in the readOFF functionality of libigl v2.5.0. A specially crafted .off file can lead to stack-based buffer overflow. An attacker can provide a malicious file to trigger this vulnerability.This vulnerability concerns the parsing of comments within the faces section of an `.off`  file processed via the `readOFF` function.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-1929
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-1929
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24686.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24686
