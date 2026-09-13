# [M] DNN's CKEditor File Uploader functionality vulnerable through Unicode obfuscation

## Summary
Severity: Medium
Advisory: CVE-2025-59547
Aliases: GHSA-cgqj-mw4m-v7hp
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-59547
Type: osv

## Details
DNN (formerly DotNetNuke) is an open-source web content management platform (CMS) in the Microsoft ecosystem. Prior to version 10.1.0, the CKEditor file upload endpoint has insufficient sanitization for filenames allowing probing network endpoints. A specially crafted request can be made to upload a file with Unicode characters, which would be translated into a path that could expose resources in the internal network of the hosted site. This issue has been patched in version 10.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59547.json
- https://github.com/dnnsoftware/Dnn.Platform/security/advisories/GHSA-cgqj-mw4m-v7hp
- https://nvd.nist.gov/vuln/detail/CVE-2025-59547
