# [H] Unauthenticated DoS by Sending Large Filename at File Upload Endpoint in netease-youdao/qanything

## Summary
Severity: High
Advisory: CVE-2024-12864
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12864
Type: osv

## Details
A Denial of Service (DoS) vulnerability was discovered in the file upload feature of netease-youdao/qanything version v2.0.0. The vulnerability is due to improper handling of form-data with a large filename in the file upload request. An attacker can exploit this vulnerability by sending a large filename, causing the server to become overwhelmed and unavailable for legitimate users. This attack does not require authentication, making it highly scalable and increasing the risk of exploitation.

## References
- https://huntr.com/bounties/365c3b9a-180c-4bb5-98d8-dbd78d93fcb7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12864.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12864
