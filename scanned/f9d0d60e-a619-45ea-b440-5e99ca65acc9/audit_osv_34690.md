# [M] CVE-2025-63914

## Summary
Severity: Medium
Advisory: CVE-2025-63914
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-24
Source: https://osv.dev/vulnerability/CVE-2025-63914
Type: osv

## Details
An issue was discovered in Cinnamon kotaemon 0.11.0. The _may_extract_zip function in the \libs\ktem\ktem\index\file\ui.py file does not check the contents of uploaded ZIP files. Although the contents are extracted into a temporary folder that is cleared before each extraction, successfully uploading a ZIP bomb could still cause the server to consume excessive resources during decompression. Moreover, if no further files are uploaded afterward, the extracted data could occupy disk space and potentially render the system unavailable. Anyone with permission to upload files can carry out this attack.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63914.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-63914
- https://github.com/Cinnamon/kotaemon
- https://github.com/WxDou/CVE-2025-63914
