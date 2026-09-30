# [H] CVE-2022-43591

## Summary
Severity: High
Advisory: CVE-2022-43591
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-01-12
Source: https://osv.dev/vulnerability/CVE-2022-43591
Type: osv

## Details
A buffer overflow vulnerability exists in the QML QtScript Reflect API of Qt Project Qt 6.3.2. A specially-crafted javascript code can trigger an out-of-bounds memory access, which can lead to arbitrary code execution. Target application would need to access a malicious web page to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1650
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2022-1650
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43591.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43591
