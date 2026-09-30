# [H] Gitea: Notification API leaks private issue metadata after access revocation

## Summary
Severity: High
Advisory: GHSA-44qc-pgvp-wx7v
CVE: CVE-2026-58419
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-44qc-pgvp-wx7v
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.4

## Details
# Summary

An information disclosure issue in the Gitea Notification API allows users who have lost access to a private repository to continue accessing private issue or pull request information through existing notification threads. Although repository information is hidden after access revocation, the `subject` field remains accessible and continues to expose private metadata.

# Details

CVE-2026-20800 was fixed in v1.25.4 to prevent users from accessing private repository information through notification APIs after their repository access had been revoked.

During testing on Gitea v1.26.2, the `repository` field in `NotificationThread` responses is correctly set to `null` after access revocation. However, the associated `subject` field remains available.

The exposed `subject` object may contain:

* Private issue or pull request titles
* Repository-related API and HTML URLs
* Issue or pull request state
* Latest comment URLs and comment identifiers

Additionally, the exposed notification data is not limited to historical information. If new comments are added to the issue or pull request while the notification remains unread, fields such as `latest_comment_url` and `updated_at` continue to change. As a result, a user whose repository access has been revoked can still observe ongoing issue or pull request activity through notification APIs.

The observed behavior suggests that access control is applied to the `repository` field but not consistently applied to the associated `subject` information.

# PoC

## Environment

* Gitea v1.26.2
* Private repository

## Steps to Reproduce

1. User `sun` creates a private repository and grants read access to user `li`.

2. User `li` subscribes to repository notifications.

3. User `sun` creates a private issue and adds a comment.

4. User `li` receives a notification (`thread_id = 14`).

5. User `sun` revokes `li`'s repository access.

6. User `li` requests:

   ```http
   GET /api/v1/repos/sun/{repo}/issues/1
   ```

   Response:

   ```text
   404 Not Found
   ```

7. User `li` requests:

   ```http
   GET /api/v1/notifications?all=true
   ```

8. User `li` requests:

   ```http
   GET /api/v1/notifications/threads/14
   ```

## Observed Result

The notification is returned successfully. The `repository` field is `null`, but the `subject` field still contains private issue metadata.

Example:

```json
{
  "id": 14,
  "repository": null,
  "subject": {
    "title": "private issue title",
    "url": "http://localhost:3000/api/v1/repos/sun/private-repo/issues/1",
    "latest_comment_url": "http://localhost:3000/api/v1/repos/sun/private-repo/issues/comments/24",
    "html_url": "http://localhost:3000/sun/private-repo/issues/1",
    "state": "open"
  }
}
```

## Expected Result

Users who no longer have access to a repository should not receive private issue or pull request information through notification APIs. The `subject` field should be removed, redacted, or otherwise protected by the same access controls applied to the `repository` field.

## Detailed PoC

https://anonymous.4open.science/r/Gitea_PoC-EC93/1_poc_notification_leak

# Impact

**Affected Endpoints**

* `GET /api/v1/notifications`
* `GET /api/v1/notifications/threads/{id}`

**Prerequisites**

* The user previously had legitimate access to the private repository.
* The notification was received before repository access was revoked.

**Impact**

* Disclosure of private issue or pull request titles.
* Disclosure of repository information through notification URLs.
* Disclosure of issue or pull request state.
* Disclosure of comment activity metadata.
* Continued visibility into issue or pull request activity after repository access has been revoked.

**Tested Version**

* Confirmed on v1.26.2.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-44qc-pgvp-wx7v
- https://nvd.nist.gov/vuln/detail/CVE-2026-58419
- https://github.com/go-gitea/gitea/pull/38108
- https://github.com/go-gitea/gitea/commit/9e84deb969aff5c1115c2984e41250f28c78451f
- https://blog.gitea.com/release-of-1.26.3-and-1.26.4
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.26.4
