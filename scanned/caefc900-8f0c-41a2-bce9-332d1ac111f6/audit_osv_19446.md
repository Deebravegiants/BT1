# [C] CVE-2021-21322

## Summary
Severity: Critical
Advisory: CVE-2021-21322
Aliases: GHSA-c4qr-gmr9-v23w
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-02
Source: https://osv.dev/vulnerability/CVE-2021-21322
Type: osv

## Details
fastify-http-proxy is an npm package which is a fastify plugin for proxying your http requests to another server, with hooks. By crafting a specific URL, it is possible to escape the prefix of the proxied backend service. If the base url of the proxied server is `/pub/`, a user expect that accessing `/priv` on the target service would not be possible. In affected versions, it is possible. This is fixed in version 4.3.1.

## References
- https://github.com/fastify/fastify-http-proxy/security/advisories/GHSA-c4qr-gmr9-v23w
- https://www.npmjs.com/package/fastify-http-proxy
- https://github.com/fastify/fastify-http-proxy/commit/02d9b43c770aa16bc44470edecfaeb7c17985016
