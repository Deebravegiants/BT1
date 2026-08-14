### Title
Unbounded reliance on `window 'load'` event permanently stalls the content-script RPC bridge - ([File: libraries/browser-extension-rpc/content.js])

### Summary
`content.js` creates a single `metadata` promise that only resolves inside a `window.addEventListener('load', ...)` callback, and the transport `'data'` handler `await`s that same promise before dispatching every inbound RPC call via `channel.call(event, options)` or `channel.sendMessage`. Because the browser `load` event depends entirely on completion of all subresources on the page, a dapp that keeps at least one subresource perpetually pending (e.g., an open `<script src=...>` to a never-completing response, or a hung iframe/image) can prevent `load` from ever firing, permanently starving every RPC request/response routed through that content script instance.

### Finding Description
In `content.js`:
```js
const metadata = new Promise((resolve) => {
  window.addEventListener('load', async () => {
    const title = getTitle()
    const icon = await getIcon()
    resolve({ title, icon })
  })
})
``` [1](#0-0) 

`metadata` is a module-scoped constant with no timeout, fallback, or alternate resolution path — its only resolver is the `load` listener. `createRPCProxy` then wires every inbound transport `'data'` event through this same promise:
```js
transport.on('data', async (event) => {
  const isResponse = !JSON.parse(event).method
  const senderMetadata = await metadata
  const options = { senderMetadata }

  if (isResponse) {
    channel.sendMessage(event, options)
  } else {
    channel.call(event, options).then(transport.write)
  }
})
``` [2](#0-1) 

Since `window.load` fires only after the document and all of its subresources (scripts, images, iframes, stylesheets) finish loading/erroring, a page under attacker control (the dapp itself) can indefinitely delay this event by embedding a resource whose network request never resolves (e.g., a streaming/never-ending response, or a `<script>` pointed at an endpoint that never completes). This is standard, well-documented browser behavior and requires no special privileges — the attacker only needs to control the page markup/resources, which is the normal dapp threat model for this bridge. As a direct consequence, `await metadata` in the `'data'` handler never returns, so `channel.call`/`channel.sendMessage` (and thus forwarding of every signing/connect RPC request and every response written back via `transport.write`) is deferred forever for that content-script/tab instance. No existing guard — no timeout, no default/fallback `senderMetadata`, no `Promise.race` — protects against this.

### Impact Explanation
The RPC bridge for the affected tab is completely and indefinitely blocked: legitimate `connect`, signing, and other wallet RPC requests initiated from that page are queued behind the unresolved `metadata` await and never delivered to the background/wallet, and any response coming back from the wallet is likewise never written back to the page via `transport.write`. This is a targeted denial of the wallet's RPC response path scoped to the malicious origin's tab, which an attacker can leverage to desynchronize timing — e.g., stall a request so that a subsequent race (double-submission, delayed approval reuse, or UI desync) becomes exploitable. This does not affect other tabs or timers, consistent with the scoped impact described.

### Likelihood Explanation
Highly feasible: the attacker fully controls the dapp page served to the user and needs only to include one subresource whose request never completes (trivial to arrange with a server that never closes the connection, or a `<script>`/`<img>` pointed at such an endpoint). No user interaction beyond visiting/connecting to the malicious dapp is required, and the condition is deterministic and repeatable every time the page is loaded.

### Recommendation
Do not gate RPC forwarding on an unbounded `window 'load'` promise. Add a bounded timeout/fallback (e.g., `Promise.race([metadata, timeoutPromise])`) so `senderMetadata` degrades to a partial/empty value after a fixed delay, and/or decouple metadata collection from the `'data'` handler so RPC calls are forwarded immediately with metadata attached asynchronously/best-effort rather than blocking the call itself.

### Proof of Concept
Integration test plan:
1. Load `content.js` in a test DOM/JSDOM environment where `window.load` is never dispatched (simulate via a pending `<script>`/`fetch` that never resolves).
2. Call `createRPCProxy({ extensionName, channelName })` and emit a transport `'data'` event containing a valid RPC method call (e.g., `{"method":"connect", ...}`).
3. Assert that `channel.call` is invoked (or `transport.write` receives a response) within a bounded time window (e.g., 5s), or that a fallback `senderMetadata` (e.g., `null`/partial) is used.
4. Expected current (failing) behavior: `channel.call` is never invoked and `transport.write` never fires because `await metadata` at line 27 of `content.js` never resolves, proving indefinite stall.

### Citations

**File:** libraries/browser-extension-rpc/content.js (L6-12)
```javascript
const metadata = new Promise((resolve) => {
  window.addEventListener('load', async () => {
    const title = getTitle()
    const icon = await getIcon()
    resolve({ title, icon })
  })
})
```

**File:** libraries/browser-extension-rpc/content.js (L25-35)
```javascript
  transport.on('data', async (event) => {
    const isResponse = !JSON.parse(event).method
    const senderMetadata = await metadata
    const options = { senderMetadata }

    if (isResponse) {
      channel.sendMessage(event, options)
    } else {
      channel.call(event, options).then(transport.write)
    }
  })
```
