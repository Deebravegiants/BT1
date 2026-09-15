# [M] CVE-2024-25569

## Summary
Severity: Medium
Advisory: CVE-2024-25569
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2024-04-25
Source: https://osv.dev/vulnerability/CVE-2024-25569
Type: osv

## Details
An out-of-bounds read vulnerability exists in the RAWCodec::DecodeBytes functionality of Mathieu Malaterre Grassroot DICOM 3.0.23. A specially crafted DICOM file can lead to an out-of-bounds read. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BZJ4IG7EXMSMPHTK5ZFASCW6MHSOVZOE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/N5HXUKUJ7SG3TK456SGUWVZ4Z5D7JKOL/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WJA7QWWZWMY4AQFR35EA7S3CFVUTOQYG/
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-1944
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-1944
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25569.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25569
