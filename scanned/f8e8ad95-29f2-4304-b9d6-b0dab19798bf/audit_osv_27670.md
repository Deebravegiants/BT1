# [M] CVE-2024-24583

## Summary
Severity: Medium
Advisory: CVE-2024-24583
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2024-05-28
Source: https://osv.dev/vulnerability/CVE-2024-24583
Type: osv

## Details
Multiple out-of-bounds read vulnerabilities exist in the readMSH functionality of libigl v2.5.0. A specially crafted .msh file can lead to an out-of-bounds read. An attacker can provide a malicious file to trigger this vulnerability.This vulnerabilitty concerns the`readMSH` function while processing `MshLoader::ELEMENT_TRI` elements.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-1928
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-1928
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24583.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24583
