# [M] Insufficient verification of authorisation when accessing subresults in thmmniii/fbs-core

## Summary
Severity: Medium
Advisory: CVE-2023-27485
Aliases: GHSA-fhq8-p3w6-mmgr
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-03-07
Source: https://osv.dev/vulnerability/CVE-2023-27485
Type: osv

## Details
thmmniii/fbs-core is an open source feedback system for students. In versions prior to 1.5.3 when querying `subresults`, it is possible to query `subresults` from other users due to insufficient authorisation. This is only possible for logged-in users and it is not possible to associate the subresults with a specific user. This bug was fixed in commit `f1ae67d8bb2`and released with version 1.5.3. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/thm-mni-ii/feedbacksystem/releases/tag/v1.5.3
- https://thm-mni-ii.github.io/feedbacksystem/api-docs/#tag/Submission/operation/getCourseTaskSubmissionSubresults
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27485.json
- https://github.com/thm-mni-ii/feedbacksystem/security/advisories/GHSA-fhq8-p3w6-mmgr
- https://nvd.nist.gov/vuln/detail/CVE-2023-27485
- https://github.com/thm-mni-ii/feedbacksystem/commit/f1ae67d8bb2286a8eb15949038473d41b1358493
