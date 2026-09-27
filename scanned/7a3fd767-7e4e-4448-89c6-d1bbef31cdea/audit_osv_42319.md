# [M] Apache CloudStack: Unauthorised comment creation and disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-66797
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-66797
Type: osv

## Details
Improper access control in CloudStack's annotation functionality allows unauthorized comment creation and disclosure.




The addAnnotation and listAnnotation APIs perform an ownership check when an entity's UUID is specified, but fail to honor its result correctly. This lets any authenticated user write annotations to, and disclose existing annotations/comments on, an entity they don't own by simply supplying its UUID.




This issue affects Apache CloudStack: from 4.15.0.0 through 4.20.3.0 and from 4.21.0.0 through 4.22.1.0.





Users are recommended to upgrade to version 4.20.3.1 or 4.22.1.1 or later, which fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66797.json
- https://lists.apache.org/thread/g6cwddtjrwbh1d56wjz4cfp3fzfm4kbc
- https://nvd.nist.gov/vuln/detail/CVE-2026-66797
