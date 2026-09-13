# [H] Tencent FaceDetection-DSFD resnet Deserialization of Untrusted Data Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-13715
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2025-13715
Type: osv

## Details
Tencent FaceDetection-DSFD resnet Deserialization of Untrusted Data Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Tencent FaceDetection-DSFD. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the resnet endpoint. The issue results from the lack of proper validation of user-supplied data, which can result in deserialization of untrusted data. An attacker can leverage this vulnerability to execute code in the context of root. Was ZDI-CAN-27197.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/13xxx/CVE-2025-13715.json
- https://github.com/Tencent/FaceDetection-DSFD/commit/a941d089d8ae2df5292a904e79d88649cb58a440
- https://nvd.nist.gov/vuln/detail/CVE-2025-13715
- https://www.zerodayinitiative.com/advisories/ZDI-25-1183/
