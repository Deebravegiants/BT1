# [M] Apache NimBLE: Buffer overflow in NimBLE MESH Bluetooth stack

## Summary
Severity: Medium
Advisory: CVE-2024-47248
CVSS: 6.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-11-26
Source: https://osv.dev/vulnerability/CVE-2024-47248
Type: osv

## Details
Buffer Copy without Checking Size of Input ('Classic Buffer Overflow') vulnerability in Apache NimBLE.

Specially crafted MESH message could result in memory corruption when non-default build configuration is used.
This issue affects Apache NimBLE: through 1.7.0.

Users are recommended to upgrade to version 1.8.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2024/11/26/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47248.json
- https://lists.apache.org/thread/z8m7jqh54xybf9kz8q2l3tz92zsj7tmz
- https://nvd.nist.gov/vuln/detail/CVE-2024-47248
- https://github.com/apache/mynewt-nimble/commit/4f75c0b3b466186beff40e8489870c6cee076aaa
