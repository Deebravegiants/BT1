# [M] CVE-2024-25580

## Summary
Severity: Medium
Advisory: CVE-2024-25580
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/CVE-2024-25580
Type: osv

## Details
An issue was discovered in gui/util/qktxhandler.cpp in Qt before 5.15.17, 6.x before 6.2.12, 6.3.x through 6.5.x before 6.5.5, and 6.6.x before 6.6.2. A buffer overflow and application crash can occur via a crafted KTX image file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SYE2NMN67DYHYJKLAKLGR64OYI7A63AH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZWTGLKC3WBDHZ5OJRSEB2QUR7XXZDLZV/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25580.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25580
- https://www.qt.io/blog/security-advisory-potential-buffer-overflow-when-reading-ktx-images
