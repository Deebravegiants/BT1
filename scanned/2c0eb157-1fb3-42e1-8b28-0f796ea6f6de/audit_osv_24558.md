# [H] CVE-2023-22845

## Summary
Severity: High
Advisory: CVE-2023-22845
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-03-30
Source: https://osv.dev/vulnerability/CVE-2023-22845
Type: osv

## Details
An out-of-bounds read vulnerability exists in the TGAInput::decode_pixel() functionality of OpenImageIO Project OpenImageIO v2.4.7.1. A specially crafted targa file can lead to information disclosure. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1708
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1708
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22845.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-22845
