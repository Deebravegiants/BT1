# [M] Header dropping in traefik

## Summary
Severity: Medium
Advisory: GHSA-m697-4v8f-55qg
CVE: CVE-2021-32813
CWE: CWE-913
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-05
Source: https://github.com/advisories/GHSA-m697-4v8f-55qg
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.4.13
- Go: `github.com/traefik/traefik` — affected >=0

## Details
# Impact

There exists a potential header vulnerability in Traefik's handling of the Connection header. Active exploitation of this issue is unlikely, as it requires that a removed header would lead to a privilege escalation, however, the Traefik team has addressed this issue to prevent any potential abuse.

# Details

If you have a chain of Traefik middlewares, and one of them sets a request header `Important-Security-Header`, then sending a request with the following Connection header will cause it to be removed before the request was sent:

```
curl 'https://example.com' -H "Connection: Important-Security-Header" -0
```

In this case, the backend does not see the request header `Important-Security-Header`.

# Patches

Traefik v2.4.x: https://github.com/traefik/traefik/releases/tag/v2.4.13

# Workarounds

No.

# For more information

If you have any questions or comments about this advisory, [open an issue](https://github.com/traefik/traefik/issues).

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-m697-4v8f-55qg
- https://nvd.nist.gov/vuln/detail/CVE-2021-32813
- https://github.com/traefik/traefik/pull/8319/commits/cbaf86a93014a969b8accf39301932c17d0d73f9
- https://github.com/traefik/traefik/releases/tag/v2.4.13
- github.com/traefik/traefik
