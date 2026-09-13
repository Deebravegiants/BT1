# [H] Nuxt Devtools has a Path Traversal: '../filedir'

## Summary
Severity: High
Advisory: GHSA-rcvg-rgf7-pppv
CVE: CVE-2024-23657
CWE: CWE-22, CWE-24
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-rcvg-rgf7-pppv
Type: github-advisory

## Affected
- npm: `@nuxt/devtools` — affected >=0 <1.3.9

## Details
### Summary
Nuxt Devtools is missing authentication on the `getTextAssetContent` RPC function which is vulnerable to path traversal.  Combined with a lack of Origin checks on the WebSocket handler,  an attacker is able to interact with a locally running devtools instance and exfiltrate data abusing this vulnerability. 

In certain configurations an attacker could leak the devtools authentication token and then abuse other RPC functions to achieve RCE. 

### Details
The `getTextAssetContent` function does not check for path traversals [(source)](https://github.com/nuxt/devtools/blob/c4f2b68281203fc3f61ffc97d9c6623fbfde46bb/packages/devtools/src/server-rpc/assets.ts#L88C48-L88C48), this could allow an attacker to read arbitrary files over the RPC WebSocket. 

The WebSocket server does not check the origin of the request [(source)](https://github.com/nuxt/devtools/blob/c4f2b68281203fc3f61ffc97d9c6623fbfde46bb/packages/devtools/src/server-rpc/index.ts#L109) leading to [CSWSH](https://portswigger.net/web-security/websockets/cross-site-websocket-hijacking). This may be intentional to allow certain configurations to work correctly.

Nuxt Devtools authentication tokens are placed within the home directory of the current user  [(source)](https://github.com/nuxt/devtools/blob/c4f2b68281203fc3f61ffc97d9c6623fbfde46bb/packages/devtools/src/dev-auth.ts#L14).

In the scenario that:
 + The user has a Nuxt3 Project running
 + Devtools is enabled and running
 + The project is placed within the users home directory.
 + The user visits a malicious webpage
 + User has authenticated with devtools at least once

The malicious webpage can connect to the Devtools WebSocket, perform a directory traversal brute force to find the authentication token, then use the *authenticated* [`writeStaticAssets` function](https://github.com/nuxt/devtools/blob/c4f2b68281203fc3f61ffc97d9c6623fbfde46bb/packages/devtools/src/server-rpc/assets.ts#L96C11-L96C28) to create a new Component, Nitro Handler or `app.vue` file which will run automatically as the file is changed.

### PoC
POC will exploit the Devtools server on localhost:3000 (you may need to manually restart the server as the restart hook does not always work).

POC: https://devtools-exploit.pages.dev

1. Create a new project with nuxt.new.
2. Place the project inside your home directory.
3. Run `pnpm run dev`.
4. Open the POC page.

The POC will:
+ Identify devtools version.
+ Leak your devtools token.
+ Create a new server handler with an insecure eval.

### Impact
+ All new Nuxt projects by default (devtools is enabled) are vulnerable to arbitrary file read.
+ Certain Nuxt configurations are vulnerable to Remote Code Execution

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-rcvg-rgf7-pppv
- https://nvd.nist.gov/vuln/detail/CVE-2024-23657
- https://github.com/nuxt/devtools/blob/c4f2b68281203fc3f61ffc97d9c6623fbfde46bb/packages/devtools/src/dev-auth.ts#L14
- https://github.com/nuxt/devtools/blob/c4f2b68281203fc3f61ffc97d9c6623fbfde46bb/packages/devtools/src/server-rpc/assets.ts#L88C48-L88C48
- https://github.com/nuxt/devtools/blob/c4f2b68281203fc3f61ffc97d9c6623fbfde46bb/packages/devtools/src/server-rpc/assets.ts#L96C11-L96C28
- https://github.com/nuxt/devtools/blob/c4f2b68281203fc3f61ffc97d9c6623fbfde46bb/packages/devtools/src/server-rpc/index.ts#L109
- https://github.com/nuxt/nuxt
- https://portswigger.net/web-security/websockets/cross-site-websocket-hijacking
