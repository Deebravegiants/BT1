# [M] CVE-2023-24473

## Summary
Severity: Medium
Advisory: CVE-2023-24473
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-03-30
Source: https://osv.dev/vulnerability/CVE-2023-24473
Type: osv

## Details
An information disclosure vulnerability exists in the TGAInput::read_tga2_header functionality of OpenImageIO Project OpenImageIO v2.4.7.1. A specially crafted targa file can lead to a disclosure of sensitive information. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1707
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1707
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24473.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-24473
