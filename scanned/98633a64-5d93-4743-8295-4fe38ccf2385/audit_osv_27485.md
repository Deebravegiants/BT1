# [H] CVE-2024-22373

## Summary
Severity: High
Advisory: CVE-2024-22373
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-25
Source: https://osv.dev/vulnerability/CVE-2024-22373
Type: osv

## Details
An out-of-bounds write vulnerability exists in the JPEG2000Codec::DecodeByStreamsCommon functionality of Mathieu Malaterre Grassroot DICOM 3.0.23. A specially crafted DICOM file can lead to a heap buffer overflow. An attacker can provide a malicious file to trigger this vulnerability.

## References
- http://www.openwall.com/lists/oss-security/2026/09/10/13
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BZJ4IG7EXMSMPHTK5ZFASCW6MHSOVZOE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/N5HXUKUJ7SG3TK456SGUWVZ4Z5D7JKOL/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WJA7QWWZWMY4AQFR35EA7S3CFVUTOQYG/
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-1935
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-1935
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/22xxx/CVE-2024-22373.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-22373
