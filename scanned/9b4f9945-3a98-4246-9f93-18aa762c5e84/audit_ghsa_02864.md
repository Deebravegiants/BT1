# [M] Improper Access Control in github.com/treeverse/lakefs

## Summary
Severity: Medium
Advisory: GHSA-m836-gxwq-j2pm
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-10-28
Source: https://github.com/advisories/GHSA-m836-gxwq-j2pm
Type: github-advisory

## Affected
- Go: `github.com/treeverse/lakefs` — affected >=0 <0.53.1

## Details
### Impact

1. [medium] A user with write permissions to a portion of a repository may use the S3 gateway to copy any object in the repository if they know its name.
1. [medium] A user with permission to write any one of tags, branches, or commits on a repository may write all of them.
1. [low] A user with permission to read any one of tags, branches, or commits on a repository may read all of them.
1. [low] A user allowed to list objects in a repository _or_ read repository meta-data may retrieve graveler information about the location on underlying storage of all objects stored in any commit that they can view.  If the user additionally has the capability to read underlying storage, they will be able to retrieve metadata associated with all objects in that commit.

### For more information

If you have any questions or comments about this advisory please:
* Email us at security@treeverse.io.
* Open an issue on https://github.com/treeverse/lakeFS/issues/new.

## References
- https://github.com/treeverse/lakeFS/security/advisories/GHSA-m836-gxwq-j2pm
- https://github.com/treeverse/lakeFS/commit/f2117281cadb14fdf9ac7fe287f84d5c10308b88
- https://github.com/treeverse/lakeFS
