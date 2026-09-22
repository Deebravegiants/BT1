# [M] Logs Debug Injection in danny-avila/librechat

## Summary
Severity: Medium
Advisory: CVE-2024-12580
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12580
Type: osv

## Details
A vulnerability in danny-avila/librechat prior to version 0.7.6 allows for logs debug injection. The parameters sessionId, fileId, userId, and file_id in the /code/download/:sessionId/:fileId and /download/:userId/:file_id APIs are not validated or filtered, leading to potential log injection attacks. This can cause distortion of monitoring and investigation information, evade detection from security systems, and create difficulties in maintenance and operation.

## References
- https://huntr.com/bounties/6e477667-dcd4-42c2-b342-a6ce09ffdeeb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12580.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12580
- https://github.com/danny-avila/librechat/commit/95d6bd2c2db4a09b308be2b96e3d5fd522c7b72a
