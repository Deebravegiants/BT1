# [M] Cloudflare Vite plugin exposes secrets over the built-in dev server

## Summary
Severity: Medium
Advisory: GHSA-4pfg-2mw5-f8jx
CVE: CVE-2025-59427
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-07-08
Source: https://github.com/advisories/GHSA-4pfg-2mw5-f8jx
Type: github-advisory

## Affected
- npm: `@cloudflare/vite-plugin` — affected >=0 <1.6.0

## Details
### Summary

Note: [originally posted on H1](https://hackerone.com/reports/3117837) but closed. Cross-posting over to here in abundance of caution instead of a public issue. 

When utilising the Cloudflare Vite plugin in its default configuration, all files are exposed by the local dev server, including files in the root directory that contain secret information such as:
- `.env`
- `.dev.vars`

### PoC
1. Create a Workers project that utilises the `@cloudflare/vite-plugin`. For example:
   - `npm create cloudflare@latest` - select Framework Starter -> React
2. Add any secret files to test if they're accessible. `echo foobar=secret > .dev.vars` for example
3. Run `npm run dev` to start the dev server (after running `npm ci` if necessary to install dependencies) and then hit the following to expose information:

`curl http://localhost:5173/.env` may expose any secrets in this file
`curl http://localhost:5173/.dev.vars` may expose any secrets in this file
`curl http://localhost:5173/package.json` may expose dependencies used by the project, potentially leading to other vulnerabilities
`curl http://localhost:5173/README.md` may expose internal documentation

### Impact

If the vite dev server is exposed on a public network, such as when a user simply uses `wrangler` to serve their application and doesn't publish to Cloudflare in production, an attacker may be able to acquire secrets that the user doesn't wish to be exposed. 

Another common scenario where this could happen is when sharing previews of an application using `cloudflared`. `npm run dev` -> share preview with `cloudflared` -> now all secrets are exposed to the public internet.

Exposing via vite is possible via:

```
npm run dev -- -- --host 0.0.0.0
```

The default configuration has no reason to expose information outside of the configured assets directory.

Example:

`curl http://somehost/.env` may expose secrets
`curl http://somehost/.dev.vars` may expose secrets
`curl http://somehost/package.json` may expose dependencies used by the project, potentially leading to other vulnerabilities
`curl http://somehost/README.md` may expose internal documentation

etc.

Information disclosure to anyone on the same network, or if the dev server is exposed such as via `cloudflared` as explored here: https://github.com/cloudflare/workers-sdk/discussions/3455#discussioncomment-6165773

## References
- https://github.com/cloudflare/workers-sdk/security/advisories/GHSA-4pfg-2mw5-f8jx
- https://nvd.nist.gov/vuln/detail/CVE-2025-59427
- https://github.com/cloudflare/workers-sdk/commit/0e500720bf70016fa4ea21fc8959c4bd764ebc38
- https://hackerone.com/reports/3117837
- https://github.com/cloudflare/workers-sdk
- https://github.com/cloudflare/workers-sdk/discussions/3455#discussioncomment-6165773
