# [M] Possible ORM Leak Vulnerability in the Harbor

## Summary
Severity: Medium
Advisory: GHSA-h27m-3qw8-3pw8
CVE: CVE-2025-30086
CWE: CWE-200, CWE-202
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-07-23
Source: https://github.com/advisories/GHSA-h27m-3qw8-3pw8
Type: github-advisory

## Affected
- Go: `github.com/goharbor/harbor` — affected >=2.13.0 <2.13.1
- Go: `github.com/goharbor/harbor` — affected >=2.4.0-rc1.1 <2.12.4
- Go: `github.com/goharbor/harbor` — affected >=0 <2.4.0-rc1.0.20250331071157-dce7d9f5cffb

## Details
### Impact

Administrator users on Harbor could exploit an ORM Leak (https://www.elttam.com/blog/plormbing-your-django-orm/) vulnerability that was present in the `/api/v2.0/users` endpoint to leak users' password hash and salt values. This vulnerability was introduced into the application because the `q` URL parameter allowed the administrator to filter users by any column, and the filter `password=~` could be abused to leak out a user's password hash character by character.

An attacker with administrator access could exploit this vulnerability to leak highly sensitive information stored on the Harbor database, as demonstrated in the attached writeup by the leaking of users' password hashes and salts. All endpoints that support the `q` URL parameter are vulnerable to this ORM leak attack, and could potentially be exploitable by lower privileged users to gain unauthorised access to other sensitive information. 


### Patches
No available

### Workarounds
NA

### References

### Credit
alex@elttam.com

## References
- https://github.com/goharbor/harbor/security/advisories/GHSA-h27m-3qw8-3pw8
- https://nvd.nist.gov/vuln/detail/CVE-2025-30086
- https://github.com/goharbor/harbor/commit/dce7d9f5cffbd0d0c5d27e7a2f816f65a930702c
- https://github.com/goharbor/harbor
- https://github.com/goharbor/harbor/releases
- https://goharbor.io/blog
- https://www.elttam.com/blog/plormbing-your-django-orm
