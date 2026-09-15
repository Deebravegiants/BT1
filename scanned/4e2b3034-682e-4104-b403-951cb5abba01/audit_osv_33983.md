# [H] Apache Mynewt NimBLE: NULL Pointer Dereference in NimBLE host HCI layer

## Summary
Severity: High
Advisory: CVE-2025-53477
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-10
Source: https://osv.dev/vulnerability/CVE-2025-53477
Type: osv

## Details
NULL Pointer Dereference vulnerability in Apache Nimble.

Missing validation of HCI connection complete or HCI command TX buffer could lead to NULL pointer dereference.
This issue requires disabled asserts and broken or bogus Bluetooth controller and thus severity is considered low.

This issue affects Apache NimBLE: through 1.8.0.

Users are recommended to upgrade to version 1.9.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/01/08/3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53477.json
- https://lists.apache.org/thread/1dxthc132hwm2tzvjblrtnschcsbw2vo
- https://nvd.nist.gov/vuln/detail/CVE-2025-53477
- https://github.com/apache/mynewt-nimble/commit/0caf9baeb271ede85fcc5237ab87ddbf938600da
- https://github.com/apache/mynewt-nimble/commit/3160b8c4c7ff8db4e0f9badcdf7df684b151e077
