# [M] OAuth2-Proxy's `--gitlab-group` GitLab Group Authorization config flag stopped working in v7.0.0

## Summary
Severity: Medium
Advisory: GHSA-652x-m2gr-hppm
CVE: CVE-2021-21411
CWE: CWE-285, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-07-30
Source: https://github.com/advisories/GHSA-652x-m2gr-hppm
Type: github-advisory

## Affected
- Go: `github.com/oauth2-proxy/oauth2-proxy/v7` — affected >=0 <7.1.0

## Details
The `--gitlab-group` flag for group-based authorization in the GitLab provider stopped working in the v7.0.0 release.

Regardless of the flag settings, authorization wasn't restricted. Additionally, any authenticated users had whichever groups were set in `--gitlab-group` added to the new `X-Forwarded-Groups` header to the upstream application.

While adding GitLab project based authorization support in #630, a bug was introduced where the user session's groups field was populated with the `--gitlab-group` config entries instead of pulling the individual user's group membership from the GitLab Userinfo endpoint. When the session groups where compared against the allowed groups for authorization, they matched improperly (since both lists were populated with the same data) so authorization was allowed.

### Impact
This impacts GitLab Provider users who relies on group membership for authorization restrictions. Any authenticated users in your GitLab environment can access your applications regardless of `--gitlab-group` membership restrictions.

### Patches
This is patched in v7.1.0

### Workarounds
There is no workaround for the Group membership bug. But `--gitlab-project` can be set to use Project membership as the authorization checks instead of groups; it is not broken.

## References
- https://github.com/oauth2-proxy/oauth2-proxy/security/advisories/GHSA-652x-m2gr-hppm
- https://nvd.nist.gov/vuln/detail/CVE-2021-21411
- https://github.com/oauth2-proxy/oauth2-proxy/commit/0279fa7dff1752f1710707dbd1ffac839de8bbfc
- https://docs.gitlab.com/ee/user/group
- https://github.com/oauth2-proxy/oauth2-proxy
- https://github.com/oauth2-proxy/oauth2-proxy/releases/tag/v7.1.0
- https://pkg.go.dev/github.com/oauth2-proxy/oauth2-proxy/v7
