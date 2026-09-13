# [H] CVE-2025-53618

## Summary
Severity: High
Advisory: CVE-2025-53618
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-53618
Type: osv

## Details
An out-of-bounds read vulnerability exists in the JPEGBITSCodec::InternalCode functionality of Grassroot DICOM 3.024. A specially crafted DICOM file can lead to an information leak. An attacker can provide a malicious file to trigger this vulnerability.The function `grayscale_convert` is called based of the value of the malicious DICOM file specifying the intended interpretation of the image pixel data

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2025-2210
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53618.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-53618
