# [M] CVE-2024-30161

## Summary
Severity: Medium
Advisory: CVE-2024-30161
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-03-24
Source: https://osv.dev/vulnerability/CVE-2024-30161
Type: osv

## Details
In Qt 6.5.4, 6.5.5, and 6.6.2, QNetworkReply header data might be accessed via a dangling pointer in Qt for WebAssembly (wasm). (Earlier and later versions are unaffected.)

## References
- https://codereview.qt-project.org/c/qt/qtbase/+/544314
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/30xxx/CVE-2024-30161.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-30161
