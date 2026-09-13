# [H] Gitea: Git LFS object reuse allows non-Code access to authorize private source objects

## Summary
Severity: High
Advisory: GHSA-2m9v-5q2g-58vq
CVE: CVE-2026-28740
CWE: CWE-639, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-2m9v-5q2g-58vq
Type: github-advisory

## Affected
- Go: `gitea.dev` — affected >=0 <1.26.3

## Details
## Summary

A user with Code write access to one repository may be able to associate an existing Git LFS object from a private source repository with their target repository, even when they do not have Code access to the source repository that currently owns the LFS object.

The issue appears to be caused by the source-object authorization check using broad repository accessibility instead of requiring Code-unit access to at least one repository that owns the requested LFS object.

## Impact

This issue breaks the expected authorization boundary between repository units.

A user who does not have Code access to a private source repository should not be able to reuse or associate Git LFS objects owned by that repository. However, because the source-object accessibility check accepts broad repository access, non-Code access such as Issues access may be sufficient for the LFS object to be treated as accessible.

If the reused object becomes downloadable through the attacker-controlled target repository after metadata association, this can result in cross-repository Git LFS content disclosure.

The target repository write authorization is still enforced. The problem is specifically in the authorization decision for whether the source LFS object is accessible and may be reused.

## Preconditions

The attacker needs:

* an authenticated Gitea account;
* Code write access to a target repository;
* non-Code access, such as Issues access, to a private source repository;
* knowledge of an existing Git LFS object OID and size from the private source repository.

## Affected Area

The issue affects the Git LFS upload/object reuse path.

Relevant paths:

```text
services/lfs/server.go
```

Relevant handlers:

```text
BatchHandler
UploadHandler
```

Both paths can call:

```go
git_model.LFSObjectAccessible(ctx, ctx.Doer, p.Oid)
```

The helper is located in:

```text
models/git/lfs.go
```

The authorization check uses:

```go
repo_model.AccessibleRepositoryCondition(user, unit.TypeInvalid)
```

When `unit.TypeInvalid` is used, the repository access condition can include broad repository access, such as organization team membership through `team_repo` and `team_user`, without requiring that the user has access to the Code unit of the source repository.

By contrast, Code-specific repository access checks use a concrete unit type and include `team_unit` validation.

## Validation

I reproduced this locally using Gitea's Go test harness.

Validated against commit:

```text
dac41a124fd34820a3c8caf3b3592ba62cd514ff
```

The PoC creates the following scenario:

1. The attacker has Code write access to the target repository.
2. The source repository is private.
3. The attacker does not have Code access to the source repository.
4. The attacker only has Issues access to the source repository through an organization team.
5. An LFS object exists in the source repository.
6. `LFSObjectAccessible(ctx, attacker, oid)` returns `true`.
7. `NewLFSMetaObject(ctx, targetRepo.ID, pointer)` successfully creates LFS metadata for the target repository.

Test result:

```text
=== RUN   TestLFSObjectAccessibleAllowsNonCodeSourceAccess
--- PASS: TestLFSObjectAccessibleAllowsNonCodeSourceAccess
PASS
ok  	gitea.dev/models/git
```

No live instance was tested. Validation was performed only against a local test database.

## Security Expectation

A user should not be allowed to reuse or associate an LFS object from a private source repository unless they have Code access to that source repository, or another permission level explicitly intended to grant access to repository file contents.

Non-Code permissions such as Issues access should not authorize access to Git LFS object content or allow Git LFS object reuse.

## Suggested Fix

`LFSObjectAccessible` should require Code-unit access to at least one repository that owns the requested LFS object.

The check should avoid using `unit.TypeInvalid` for this source-object authorization decision. A Code-specific repository access condition should be used instead.

A regression test should cover:

* private source repository;
* user has Issues-only access to the source repository;
* user does not have Code access to the source repository;
* user has Code write access to the target repository;
* known LFS object exists in the source repository;
* object reuse must be rejected unless the user has Code access to the source repository.

## Suggested Severity

Suggested severity: Medium to High.

The severity depends on whether the associated LFS object becomes downloadable through the target repository after reuse.

If the object becomes downloadable through the target repository, the issue should be considered High because it can lead to cross-repository Git LFS content disclosure.

Suggested CVSS v3.1 if content disclosure is confirmed:

```text
CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N
```

Rationale:

* network reachable through Git LFS endpoints;
* requires authentication;
* requires knowledge of the LFS object OID and size;
* no user interaction required;
* breaks repository-level authorization expectations;
* primary impact is confidentiality of private Git LFS content;
* limited integrity impact through unauthorized LFS metadata association in the target repository.

## Evidence

I can provide the local regression test and passing test log privately if needed.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-2m9v-5q2g-58vq
- https://nvd.nist.gov/vuln/detail/CVE-2026-28740
- https://github.com/go-gitea/gitea/pull/38050
- https://github.com/go-gitea/gitea/commit/1c7b7ea72df7cf81e88b8e09049608254d32e56e
- https://github.com/go-gitea/gitea/commit/7b4a1a1a118501b9d0260301dfed7f52dfc36ee9
- https://blog.gitea.com/release-of-1.26.3-and-1.26.4
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.26.3
