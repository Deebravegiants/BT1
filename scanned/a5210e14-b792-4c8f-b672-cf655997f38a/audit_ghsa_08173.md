# [M] Gogs Allows Cross-Repository Comment Deletion via DeleteComment

## Summary
Severity: Medium
Advisory: GHSA-jj5m-h57j-5gv7
CVE: CVE-2026-25120
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-jj5m-h57j-5gv7
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.0

## Details
# IDOR: Cross-Repository Comment Deletion via DeleteComment

## Summary

The `POST /:owner/:repo/issues/comments/:id/delete` endpoint does not verify that the comment belongs to the repository specified in the URL. This allows a repository administrator to delete comments from any other repository by supplying arbitrary comment IDs, bypassing authorization controls.

## Vulnerability Details

| Field | Value |
|-------|-------|
| Affected File | `internal/route/repo/issue.go` |
| Affected Function | `DeleteComment` (lines 955-968) |
| Secondary File | `internal/database/comment.go` |
| Secondary Function | `DeleteCommentByID` (lines 505-520) |

## Root Cause

The vulnerability exists due to insufficient authorization validation in the comment deletion flow:

### 1. Missing Repository Ownership Check in DeleteComment

In `internal/route/repo/issue.go`, the function retrieves a comment by ID without verifying repository ownership:

```go
func DeleteComment(c *context.Context) {
    comment, err := database.GetCommentByID(c.ParamsInt64(":id"))
    if err != nil {
        c.NotFoundOrError(err, "get comment by ID")
        return
    }

    // Only checks if user is comment poster OR admin of the CURRENT repo (from URL)
    if c.UserID() != comment.PosterID && !c.Repo.IsAdmin() {
        c.NotFound()
        return
    } else if comment.Type != database.CommentTypeComment {
        c.Status(http.StatusNoContent)
        return
    }

    // No verification that comment.IssueID belongs to c.Repo.Repository.ID!
    if err = database.DeleteCommentByID(c.User, comment.ID); err != nil {
        c.Error(err, "delete comment by ID")
        return
    }

    c.Status(http.StatusOK)
}
```

### 2. Database Layer Performs No Authorization

In `internal/database/comment.go`, the deletion function performs no repository validation:

```go
func DeleteCommentByID(doer *User, id int64) error {
    comment, err := GetCommentByID(id)
    if err != nil {
        if IsErrCommentNotExist(err) {
            return nil
        }
        return err
    }

    // Directly deletes without checking repository ownership
    sess := x.NewSession()
    defer sess.Close()
    if err = sess.Begin(); err != nil {
        return err
    }

    if _, err = sess.ID(comment.ID).Delete(new(Comment)); err != nil {
        // ...
    }
    // ...
}
```

## Proof of Concept

### Prerequisites

1. Two users: **Alice** (attacker) and **Bob** (victim)
2. Alice is admin of `alice/attacker-repo`
3. Bob has created an issue with a comment on `bob/victim-repo`
4. Attacker needs to obtain the comment ID from victim's repository (e.g., ID: 42)

### HTTP Request

```http
POST /alice/attacker-repo/issues/comments/42/delete HTTP/1.1
Host: gogs.example.com
Cookie: i_like_gogs=<alice_session_token>

```

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-jj5m-h57j-5gv7
- https://nvd.nist.gov/vuln/detail/CVE-2026-25120
- https://github.com/gogs/gogs/commit/1b226ca48dc8b3e95cc1c41229d72819c960a1b7
- https://github.com/gogs/gogs
