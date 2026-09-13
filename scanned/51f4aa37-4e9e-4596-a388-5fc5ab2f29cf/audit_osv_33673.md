# [H] CVE-2025-48429

## Summary
Severity: High
Advisory: CVE-2025-48429
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-48429
Type: osv

## Details
An out-of-bounds read vulnerability exists in the RLECodec::DecodeByStreams functionality of Grassroot DICOM 3.024. A specially crafted DICOM file can lead to leaking heap data. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2025-2214
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2025-2214
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48429.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-48429
