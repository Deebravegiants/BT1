# [M] Traefik vulnerable to Open Redirect via handling of X-Forwarded-Prefix header

## Summary
Severity: Medium
Advisory: GHSA-6qq8-5wq3-86rp
CVE: CVE-2020-15129
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-11
Source: https://github.com/advisories/GHSA-6qq8-5wq3-86rp
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik` — affected >=1.5.0-rc5 <1.7.26
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.3.0-rc6
- Go: `github.com/containous/traefik` — affected >=1.5.0-rc5 <1.7.26
- Go: `github.com/containous/traefik/v2` — affected >=0 <2.2.8
- Go: `github.com/traefik/traefik/v2` — affected >=2.3.0-rc1 <2.3.0-rc6
- Go: `github.com/containous/traefik/v2` — affected >=2.3.0-rc1 <2.3.0-rc3
- Go: `github.com/traefik/traefik/api` — affected >=1.5.0-rc5 <1.7.26
- Go: `github.com/traefik/traefik/v2/pkg/api` — affected >=0 <2.3.0-rc6
- Go: `github.com/traefik/traefik/v2/pkg/api` — affected >=2.3.0-rc1 <2.3.0-rc6
- Go: `github.com/containous/traefik/api` — affected >=1.5.0-rc5 <1.7.26
- Go: `github.com/containous/traefik/v2/pkg/api` — affected >=0 <2.2.8
- Go: `github.com/containous/traefik/v2/pkg/api` — affected >=2.3.0-rc1 <2.3.0-rc3

## Details
## Summary

There exists a potential open redirect vulnerability in Traefik's handling of the `X-Forwarded-Prefix` header. Active Exploitation of this issue is unlikely as it would require active header injection, however the Traefik team addressed this issue nonetheless to prevent abuse in e.g. cache poisoning scenarios.

## Details

The Traefik API dashboard component doesn't validate that the value of the header `X-Forwarded-Prefix` is a site relative path and will redirect to any header provided URI.

e.g.

```
$ curl --header 'Host:traefik.localhost' --header 'X-Forwarded-Prefix:https://example.org' 'http://localhost:8081'
<a href="https://example.org/dashboard/">Found</a>.`
```

### Impact
A successful exploitation of an open redirect can be used to entice victims to disclose sensitive information.

### Workarounds

By using the `headers` middleware, the request header `X-Forwarded-Prefix` value can be overridden by the value `.` (dot)

- https://docs.traefik.io/v2.2/middlewares/headers/#customrequestheaders
- https://docs.traefik.io/v1.7/basics/#custom-headers

### For more information

If you have any questions or comments about this advisory, open an issue in [Traefik](https://github.com/containous/traefik/issues).

## Credit

This issue was found by the GitHub Application Security Team and reported on behalf of the GHAS by the GitHub Security Lab Team.

## References
- https://github.com/containous/traefik/security/advisories/GHSA-6qq8-5wq3-86rp
- https://nvd.nist.gov/vuln/detail/CVE-2020-15129
- https://github.com/containous/traefik/pull/7109
- https://github.com/containous/traefik/commit/cfa04c300c5db95ae8a52c31a9d973b6dd9c2254
- https://github.com/containous/traefik/commit/e63db782c11c7b8bfce30be4c902e7ef8f9f33d2
- https://github.com/traefik/traefik/commit/e2c5f3712f68993de8ed3cb30da9ec0aa11acb09
- https://github.com/containous/traefik/releases/tag/v1.7.26
- https://github.com/containous/traefik/releases/tag/v2.2.8
- https://github.com/containous/traefik/releases/tag/v2.3.0-rc3
- https://github.com/traefik/traefik
