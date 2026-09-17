# [M] Apache NimBLE: Lack of input sanitization leading to out-of-bound reads in multiple advertisement handler

## Summary
Severity: Medium
Advisory: CVE-2024-47249
CVSS: 5.0 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-11-26
Source: https://osv.dev/vulnerability/CVE-2024-47249
Type: osv

## Details
Improper Validation of Array Index vulnerability in Apache NimBLE.

Lack of input validation for HCI events from controller could result in out-of-bound memory corruption and crash.
This issue requires broken or bogus Bluetooth controller and thus severity is considered low.
This issue affects Apache NimBLE: through 1.7.0.

Users are recommended to upgrade to version 1.8.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2024/11/26/3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47249.json
- https://lists.apache.org/thread/7ckxw6481dp68ons627pjcb27c75n0mq
- https://nvd.nist.gov/vuln/detail/CVE-2024-47249
- https://github.com/apache/mynewt-nimble/commit/f39330866a85fa4de49246e9d21334bc8d14f0a1
