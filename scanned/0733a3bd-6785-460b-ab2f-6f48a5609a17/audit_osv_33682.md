# [M] Apache NuttX RTOS: fs/vfs/fs_rename: use after free

## Summary
Severity: Medium
Advisory: CVE-2025-48769
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-01-01
Source: https://osv.dev/vulnerability/CVE-2025-48769
Type: osv

## Details
Use After Free vulnerability was discovered in fs/vfs/fs_rename code of the Apache NuttX RTOS, that due recursive implementation and single buffer use by two different pointer variables allowed arbitrary user provided size buffer reallocation and write to the previously freed heap chunk, that in specific cases could cause unintended virtual filesystem rename/move operation results.

This issue affects Apache NuttX RTOS: from 7.20 before 12.11.0.

Users of virtual filesystem based services with write access especially when exposed over the network (i.e. FTP) are affected and recommended to upgrade to version 12.11.0 that fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/12/31/11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48769.json
- https://lists.apache.org/thread/7m83v11ldfq7bvw72n9t5sccocczocjn
- https://nvd.nist.gov/vuln/detail/CVE-2025-48769
- https://github.com/apache/nuttx/pull/16455
