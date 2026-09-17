# [M] Function-Level Access Control Vulnerability Allows Unauthorized Modification of Student Data in Unifiedtransform

## Summary
Severity: Medium
Advisory: CVE-2024-12307
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-12-09
Source: https://osv.dev/vulnerability/CVE-2024-12307
Type: osv

## Details
A function-level access control vulnerability in Unifiedtransform version 2.0 and potentially earlier versions allows teachers to modify student personal data without proper authorization. The vulnerability exists due to missing access control checks in the student editing functionality. At the time of publication of the CVE no patch is available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12307.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12307
- https://github.com/changeweb/Unifiedtransform
- https://huntr.com/bounties/90a7299e-9233-43fd-b666-7375c4fdbb3c
