# [H] Nautobot vulnerable to exposure of hashed user passwords via REST API

## Summary
Severity: High
Advisory: GHSA-r2hw-74xv-4gqp
CVE: CVE-2023-46128
CWE: CWE-200, CWE-312, CWE-359
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-24
Source: https://github.com/advisories/GHSA-r2hw-74xv-4gqp
Type: github-advisory

## Affected
- PyPI: `nautobot` — affected >=2.0.0 <2.0.3

## Details
### Impact

In Nautobot 2.0.x, certain REST API endpoints, in combination with the `?depth=<N>` query parameter, can expose hashed user passwords as stored in the database to any authenticated user with access to these endpoints. 

> The passwords are *not* exposed in plaintext. 
> Nautobot 1.x is *not* affected by this vulnerability.

Example:

```
GET /api/users/permissions/?depth=1

HTTP 200 OK
API-Version: 2.0
Allow: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept
```

```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "28ea85e4-5039-4389-94f1-9a3e1c787149",
            "object_type": "users.objectpermission",
            "display": "Run Job",
            "url": "http://localhost:8080/api/users/permissions/28ea85e4-5039-4389-94f1-9a3e1c787149/",
            "natural_slug": "run-job_28ea",
            "object_types": [
                "extras.job"
            ],
            "name": "Run Job",
            "description": "",
            "enabled": true,
            "actions": [
                "run",
                "view"
            ],
            "constraints": null,
            "groups": [
                {
                    "id": 1,
                    "object_type": "auth.group",
                    "display": "A Group",
                    "url": "http://localhost:8080/api/users/groups/1/",
                    "natural_slug": "a-group_1",
                    "name": "A Group"
                }
            ],
            "users": [
                {
                    "id": "e73288e2-1326-4bfb-8fea-041290dd7473",
                    "object_type": "users.user",
                    "display": "admin",
                    "url": "http://localhost:8080/api/users/users/e73288e2-1326-4bfb-8fea-041290dd7473/",
                    "natural_slug": "admin_e732",
                    "password": "pbkdf2_sha256$260000$jQb7hA48HYJ0MLWQgOZiBl$b72+gz6SpZiRpxceRQfT5Zv/aUac0eJ4NdBTZ8ECOow=",
                    "last_login": "2023-10-18T14:19:08.780857Z",
                    "is_superuser": true,
                    "username": "admin",
                    "first_name": "",
                    "last_name": "",
                    "email": "",
                    "is_staff": true,
                    "is_active": true,
                    "date_joined": "2023-10-18T14:18:55.854023Z",
                    "config_data": {}
                }
            ]
        }
    ]
}
```

> Note the "password" field present in the nested `"users"` data.

This information is not exposed during direct access to the `/api/users/users/` endpoint, but can be exposed through any endpoint which contains a nested reference to User object(s) when an appropriate `?depth=<N>` query parameter is specified. Known impacted endpoints include:

- `/api/dcim/rack-reservations/?depth=1`(or any greater `depth` value)
- `/api/extras/job-results/?depth=1` (or any greater `depth` value)
- `/api/extras/notes/?depth=1` (or any greater `depth` value)
- `/api/extras/object-changes/?depth=1` (or any greater `depth` value)
- `/api/extras/scheduled-jobs/?depth=1` (or any greater `depth` value)
- `/api/users/permissions/?depth=1` (or any greater `depth` value)

but this is not necessarily an exhaustive list. 

> Plugin REST API endpoints for any models with a foreign key to the User model may also be impacted by this issue.

> The patch identified below mitigates the issue for both Nautobot core REST APIs and plugin REST APIs; no code change in plugins is required to address this issue.

### Patches

Refer to https://github.com/nautobot/nautobot/pull/4692 for the patch that resolved this issue.

### Workarounds

Upgrading to v2.0.3 or later, or applying the above patch, is the preferred workaround for this issue; while it could also be partially mitigated by updating permissions to deny user access to the above list of impacted REST API endpoints, that is not recommended as other endpoints may also expose this issue until patched.

### References

https://github.com/nautobot/nautobot/pull/4692

## References
- https://github.com/nautobot/nautobot/security/advisories/GHSA-r2hw-74xv-4gqp
- https://nvd.nist.gov/vuln/detail/CVE-2023-46128
- https://github.com/nautobot/nautobot/pull/4692
- https://github.com/nautobot/nautobot/commit/1ce8e5c658a075c29554d517cd453675e5d40d71
- https://github.com/nautobot/nautobot
- https://github.com/pypa/advisory-database/tree/main/vulns/nautobot/PYSEC-2023-220.yaml
