# [H] Apache NimBLE: Denial of service in NimBLE Bluetooth stack

## Summary
Severity: High
Advisory: CVE-2024-24746
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-06
Source: https://osv.dev/vulnerability/CVE-2024-24746
Type: osv

## Details
Loop with Unreachable Exit Condition ('Infinite Loop') vulnerability in Apache NimBLE. 

Specially crafted GATT operation can cause infinite loop in GATT server leading to denial of service in Bluetooth stack or device.

This issue affects Apache NimBLE: through 1.6.0.
Users are recommended to upgrade to version 1.7.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2024/04/05/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24746.json
- https://lists.apache.org/thread/bptkzc0o2ymjk8qqzqdmy39kcmh27078
- https://nvd.nist.gov/vuln/detail/CVE-2024-24746
- https://github.com/apache/mynewt-nimble/commit/d42a0ebe6632bd0c318560e4293a522634f60594
