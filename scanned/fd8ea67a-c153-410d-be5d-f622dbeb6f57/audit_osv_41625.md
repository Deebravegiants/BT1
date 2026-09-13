# [C] Apache CloudStack: Improper access control in Kubernetes Service (CKS) cluster manipulation

## Summary
Severity: Critical
Advisory: CVE-2026-62440
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-62440
Type: osv

## Details
Improper Access Control vulnerability in Apache CloudStack's Kubernetes Service (CKS) plugin, allowing cross-tenant manipulation of the Kubernetes cluster while adding and removing nodes.

This issue affects Apache CloudStack: from 4.21.0.0 through 4.22.1.0.

Users are recommended to upgrade to version 4.22.1.1 or later, which fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62440.json
- https://lists.apache.org/thread/g6cwddtjrwbh1d56wjz4cfp3fzfm4kbc
- https://nvd.nist.gov/vuln/detail/CVE-2026-62440
