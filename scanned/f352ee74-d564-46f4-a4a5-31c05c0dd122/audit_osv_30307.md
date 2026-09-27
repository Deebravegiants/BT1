# [H] Apache Traffic Server: Valid Host field value can cause crashes

## Summary
Severity: High
Advisory: CVE-2024-50305
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-14
Source: https://osv.dev/vulnerability/CVE-2024-50305
Type: osv

## Details
Valid Host header field can cause Apache Traffic Server to crash on some platforms.

This issue affects Apache Traffic Server: from 9.2.0 through 9.2.5.

Users are recommended to upgrade to version 9.2.6, which fixes the issue, or 10.0.2, which does not have the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50305.json
- https://lists.apache.org/thread/y15fh6c7kyqvzm0f9odw7c5jh4r4np0y
- https://nvd.nist.gov/vuln/detail/CVE-2024-50305
