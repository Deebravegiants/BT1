# [H] Gitea: Fork Synchronization Continues After Parent Repository Changes from Public to Private

## Summary
Severity: High
Advisory: GHSA-wrf9-r3h7-7x5v
CVE: CVE-2026-24451
CWE: CWE-200, CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-wrf9-r3h7-7x5v
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.3

## Details
### Summary

The `POST /api/v1/repos/{owner}/{repo}/merge-upstream` endpoint continues to synchronize commits from a parent repository after the parent repository has been changed from public to private.

A fork created while the parent repository was public can still receive commits made after the parent repository becomes private. As a result, content added during the private period becomes available through the fork repository after synchronization.

### Details

Gitea provides the `merge-upstream` API to synchronize a fork with its parent repository.

A typical workflow is:

1. A repository is public.
2. Another user creates a fork.
3. The fork owner uses `merge-upstream` to receive updates from the parent repository.

However, if the parent repository is later changed from public to private, the synchronization endpoint continues to import new commits from the parent repository into the fork.

In testing on Gitea 1.26.2, a fork owner who can no longer directly access the parent repository is still able to synchronize newly created commits from the parent repository into the fork by calling `merge-upstream`.

As a result, commits created after the visibility change can be propagated into the fork through the normal fork synchronization workflow.

### PoC

#### Proof-of-Concept Code

https://anonymous.4open.science/r/Gitea_PoC-EC93/4_poc_merge_upstream

#### PoC Details

1. User `alice` creates a public repository `alice/P`.
2. User `bob` forks the repository, creating `bob/P`.
3. `alice` changes `alice/P` from public to private.
4. Verify that `bob` can no longer directly access the parent repository:

```http
GET /api/v1/repos/alice/P
```

Response:

```http
404 Not Found
```

```http
GET /api/v1/repos/alice/P/contents/README.md
```

Response:

```http
404 Not Found
```

5. While the repository is private, `alice` commits a new file:

```text
secret.txt
```

6. Verify that `bob` cannot directly access the new file from the parent repository:

```http
GET /api/v1/repos/alice/P/contents/secret.txt
```

Response:

```http
404 Not Found
```

7. `bob` synchronizes the fork:

```http
POST /api/v1/repos/bob/P/merge-upstream
```

Response:

```http
200 OK
```

8. The newly added file is now available through the fork repository:

```http
GET /api/v1/repos/bob/P/contents/secret.txt
```

Response:

```http
200 OK
```

The attached PoC reproduces the behavior end-to-end.

As a control test, attempting to access the private-period commit directly through the fork's Git API before synchronization fails:

```http
GET /api/v1/repos/bob/P/git/commits/<private-period-commit-sha>
```

Response:

```http
404 Not Found
```

This indicates that the commit becomes available in the fork only after the `merge-upstream` operation synchronizes it from the parent repository.

### Impact

A fork created while a repository is public can continue receiving updates from the parent repository after the parent repository is changed to private.

Consequently, content committed after the visibility change may become available through fork synchronization even when the fork owner can no longer directly access the parent repository.

The impact is limited to content that is synchronized from the parent repository into the affected fork. The issue does not allow modification of the parent repository or access to repositories that were never forked.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-wrf9-r3h7-7x5v
- https://nvd.nist.gov/vuln/detail/CVE-2026-24451
- https://github.com/go-gitea/gitea/pull/38151
- https://blog.gitea.com/release-of-1.26.3-and-1.26.4
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.26.3
