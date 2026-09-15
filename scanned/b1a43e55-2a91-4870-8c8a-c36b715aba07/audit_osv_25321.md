# [M] Missing Access Control allows User to move and duplicate tasks in Kanboard

## Summary
Severity: Medium
Advisory: CVE-2023-33968
Aliases: GHSA-gf8r-4p6m-v8vr
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-06-05
Source: https://osv.dev/vulnerability/CVE-2023-33968
Type: osv

## Details
Kanboard is open source project management software that focuses on the Kanban methodology. Versions prior to 1.2.30 are subject to a missing access control vulnerability that allows a user with low privileges to create or transfer tasks to any project within the software, even if they have not been invited or the project is personal. The vulnerable features are `Duplicate to project` and `Move to project`, which both utilize the `checkDestinationProjectValues()` function to check his values. This issue has been addressed in version 1.2.30. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33968.json
- https://github.com/kanboard/kanboard/security/advisories/GHSA-gf8r-4p6m-v8vr
- https://nvd.nist.gov/vuln/detail/CVE-2023-33968
- https://github.com/kanboard/kanboard/commit/c20be8f5fa26e54005a90c645e80b11481a65053
