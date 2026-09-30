# [H] Gogs Missing Authorization in Attachment Download

## Summary
Severity: High
Advisory: GHSA-p9f5-h3rx-j5qw
CVE: CVE-2026-52799
CWE: CWE-639, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-p9f5-h3rx-j5qw
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
## Summary

In Gogs 0.14.1, `GET /attachments/:uuid` returns the raw attachment file **without verifying whether the requester has view permission for the associated Issue/Comment/Release or the repository**.
In a test environment with `REQUIRE_SIGNIN_VIEW = false`, we confirmed that **an unauthenticated user can download attachments belonging to a private repository**.

## Description

`/attachments/:uuid` retrieves an attachment record solely by the UUID provided in the URL and returns the corresponding local file **without performing any authorization checks** against the attachment’s parent object (Issue/Comment/Release) or the repository it belongs to. As a result, even attachments under private repositories can be downloaded by an unauthenticated user (or a user without proper permissions) as long as the UUID is known.

Relevant code (internal/cmd/web.go:306):

```go
m.Get("/attachments/:uuid", func(c *context.Context) {
	attach, err := database.GetAttachmentByUUID(c.Params(":uuid"))
	if err != nil {
		c.NotFoundOrError(err, "get attachment by UUID")
		return
	} else if !com.IsFile(attach.LocalPath()) {
		c.NotFound()
		return
	}

	fr, err := os.Open(attach.LocalPath())
	if err != nil {
		c.Error(err, "open attachment file")
		return
	}
	defer fr.Close()

	c.Header().Set("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; sandbox")
	c.Header().Set("Cache-Control", "public,max-age=86400")
	c.Header().Set("Content-Disposition", fmt.Sprintf(`inline; filename="%s"`, attach.Name))

	if _, err = io.Copy(c.Resp, fr); err != nil {
		c.Error(err, "copy from file to response")
		return
	}
})
```

The UUID lookup itself also performs **no validation tied to repository visibility or user permissions**. Authorization is not enforced at this layer.

Relevant code (internal/database/attachment.go:124):

```go
// GetAttachmentByUUID returns attachment by given UUID.
func GetAttachmentByUUID(uuid string) (*Attachment, error) {
	return getAttachmentByUUID(x, uuid)
}
```

## Preconditions

* The attacker knows the target attachment’s UUID (i.e., the attachment URL).
* For unauthenticated exploitation: `[auth] REQUIRE_SIGNIN_VIEW = false`.
* Even when `REQUIRE_SIGNIN_VIEW = true`, exploitation may still be possible because the handler does not check repository-level permissions; a user who can log in but lacks access to the target repository may still retrieve the attachment.

## Steps to Reproduce

1. Log in as an administrator and create a private repository, e.g. `myadmin/idor-attach-1770724346-1a13bb`.
2. Add an attachment to an Issue in that repository and note the attachment UUID
   (example UUID used during testing: `f06d90f8-5b62-4c10-ac8d-f11fdf870b57`).
3. Log out and access the following as an unauthenticated user:

* The repository page → 404 Not Found
<img width="1702" height="758" alt="image" src="https://github.com/user-attachments/assets/8fdb1d92-cfc3-4ef8-977e-60ec13f792df" />

* The Issue page under that repository → 404 Not Found
<img width="1983" height="546" alt="image" src="https://github.com/user-attachments/assets/c44c5e69-8ca2-4ea6-a071-62302b7e896f" />

* `GET /attachments/<uuid>` → **the attachment file is successfully downloaded**
<img width="2007" height="378" alt="image" src="https://github.com/user-attachments/assets/23950ac6-6b3a-42f8-a06b-b9e0cf508d24" />



## Minimum Required Privileges

* `REQUIRE_SIGNIN_VIEW = false`: none (works without authentication).
* `REQUIRE_SIGNIN_VIEW = true`: only the ability to log in (repository view permission is not required in practice).

## Impact

* Confidential information attached to private repositories or restricted Issues/Releases may be disclosed.

  * Examples include credentials, cryptographic keys, personal data, internal documents, or unpublished source code fragments.
* While the severity depends on the attachment contents, attachments frequently contain sensitive data, making the potential impact high.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-p9f5-h3rx-j5qw
- https://nvd.nist.gov/vuln/detail/CVE-2026-52799
- https://github.com/gogs/gogs/pull/8320
- https://github.com/gogs/gogs/commit/d3ca23f9f33d5710472a775d6dcd3a7bb128bb05
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
