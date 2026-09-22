# [C] Apache Traffic Server: Server process can fail to drop privilege

## Summary
Severity: Critical
Advisory: CVE-2024-50306
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-11-14
Source: https://osv.dev/vulnerability/CVE-2024-50306
Type: osv

## Details
Unchecked return value can allow Apache Traffic Server to retain privileges on startup.

This issue affects Apache Traffic Server: from 9.2.0 through 9.2.5, from 10.0.0 through 10.0.1.

Users are recommended to upgrade to version 9.2.6 or 10.0.2, which fixes the issue.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00018.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50306.json
- https://lists.apache.org/thread/y15fh6c7kyqvzm0f9odw7c5jh4r4np0y
- https://nvd.nist.gov/vuln/detail/CVE-2024-50306
