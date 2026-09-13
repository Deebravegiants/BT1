# [H] Apache Kvrocks: The server was crashed by the negative offset

## Summary
Severity: High
Advisory: CVE-2025-26413
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-22
Source: https://osv.dev/vulnerability/CVE-2025-26413
Type: osv

## Details
Improper Input Validation vulnerability in Apache Kvrocks.

The SETRANGE command didn't check if the `offset` input is a positive integer and use it as an index
of a string. So it will cause the server to crash due to its index is  out of range.
This issue affects Apache Kvrocks: through 2.11.1.

Users are recommended to upgrade to version 2.12.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/04/22/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26413.json
- https://lists.apache.org/thread/388743qrr8yq8qm0go8tls6rf1kog8dw
- https://nvd.nist.gov/vuln/detail/CVE-2025-26413
