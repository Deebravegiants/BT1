# [H] Apache CloudStack: MinIO policy remains intact on bucket deletion

## Summary
Severity: High
Advisory: CVE-2025-66467
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2025-66467
Type: osv

## Details
Missing MinIO policy cleanup on bucket deletion via Apache CloudStack allows users to retain access to buckets which they previously owned. If another user creates a new bucket with the same name, the previous owners can gain unauthorized read and write access to it by using the previously generated access and secret keys.

Users are recommended to upgrade to Apache CloudStack versions 4.20.3.0 or 4.22.0.1, or later, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/05/09/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66467.json
- https://lists.apache.org/thread/n8mt5b7wkpysstb8w7rr9f02kc5cq2xm
- https://nvd.nist.gov/vuln/detail/CVE-2025-66467
