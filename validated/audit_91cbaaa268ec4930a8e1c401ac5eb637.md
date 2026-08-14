### Title
`getIcon()` can hang forever on a stalled favicon load, permanently blocking the RPC bridge in `content.js` - (File: `libraries/browser-extension-rpc/src/metadata.js`)

### Summary
`getIconData()` in `metadata.js` creates an `Image` and resolves its promise only from the `load` or `error` events, with no timeout guard. An attacker-controlled page can serve (or link to) a favicon resource that never completes the HTTP response (neither firing `load` nor `error`), which leaves the `metadata` promise in `content.js` permanently unresolved. Because `transport.on('data')` awaits `metadata` before calling `channel.call`/`channel.sendMessage`, every RPC message on that tab is blocked indefinitely.

### Finding Description
`getIcon()` picks a favicon URL from the page's own `<link rel="icon">` tags (fully attacker-controlled on an attacker page) or falls back to `${origin}/favicon.ico`: [1](#0-0) 

That URL is loaded via `getIconData()`, which only resolves on the image's `load` or `error` events: [2](#0-1) 

If the attacker's server never finishes responding (e.g., slow-loris style: opens the connection, sends headers but never completes/never closes the body), the browser's `Image` element fires neither `load` nor `error` — it simply stays pending. There is no `setTimeout`/abort fallback in `getIconData`, so the returned promise never settles.

This promise is awaited directly in `content.js`: [3](#0-2) 

and the resulting `metadata` promise is awaited on every single incoming transport message before any RPC dispatch happens: [4](#0-3) 

Since `await metadata` sits before both the `channel.call(...)` (request) and `channel.sendMessage(...)` (response) branches, a stalled favicon load blocks all subsequent RPC traffic for that tab — including responses to already-pending requests and any new consent/approval flows initiated afterward.

Note: the `img.crossOrigin = 'anonymous'` setting does prevent silent canvas-tainting via a successful `load` (a CORS-rejected image fires `error`, not `load`), so the "tainted canvas SecurityError inside `ctx.getImageData`" branch of the question is not really reachable — but the "never fires load or error" branch is fully reachable and unguarded.

### Impact Explanation
Any dapp/site the user visits (fully unprivileged, no special permissions needed) can control its own favicon `<link>` tags or serve a hanging `favicon.ico`, causing the extension's content script to stall on `getIcon()` forever. This creates a persistent denial-of-service of the wallet's RPC bridge for that specific tab: all future `channel.call`/`channel.sendMessage` dispatches on that tab's transport are blocked, since they wait on the same unresolved `metadata` promise. This can also mask a hung approval/consent flow as an apparently normal, unresponsive state, making it harder for a user to notice something is wrong versus a legitimately slow page.

### Likelihood Explanation
- Preconditions are trivial and require no privileged access: only an ordinary page load with attacker-controlled `<link rel="icon">` markup (or control of the origin's `/favicon.ico` endpoint).
- No special browser features or race conditions are required — a server that simply never finishes the image response is sufficient.
- The bug is fully deterministic/repeatable: it triggers on every page load from that origin.

### Recommendation
Add a timeout/abort guard to `getIconData()` (e.g., `Promise.race` against a `setTimeout` that resolves with `null`, and set `img.src = ''`/remove listeners to cancel the pending load), and wrap the `ctx.getImageData` call in try/catch to also resolve `null` on `SecurityError`. Additionally, decouple the RPC dispatch path in `content.js` from `metadata` resolution — e.g., use `Promise.race` with a bounded timeout when reading `senderMetadata`, or dispatch/queue RPC messages independently of metadata computation so a stalled icon fetch cannot block `channel.call`/`channel.sendMessage`.

### Proof of Concept
Unit test plan (Jest, mocking `Image`):
```js
test('metadata never resolves and blocks RPC dispatch when favicon image never loads or errors', async () => {
  // Mock global Image to never fire 'load' or 'error'
  class HangingImage {
    addEventListener() {} // no-op, never calls load
    set src(_) {}
    set crossOrigin(_) {}
  }
  global.Image = HangingImage
  document.body.innerHTML = '<link rel="icon" href="https://attacker.example/favicon.ico">'

  jest.useFakeTimers()

  const { createRPCProxy } = require('../content.js')
  // ... set up mocked channels/transport per existing test harness

  const dataHandlerSettled = jest.fn()
  transport.emit('data', JSON.stringify({ method: 'someMethod', id: 1, params: [] }))
    .then(dataHandlerSettled)

  await jest.advanceTimersByTimeAsync(60_000) // wait well beyond any reasonable timeout

  expect(dataHandlerSettled).not.toHaveBeenCalled() // metadata/transport handling never settled
})
```
Expected (current, buggy) behavior: the assertion passes, proving `metadata` and the `transport.on('data')` handler never settle, confirming the permanent RPC-bridge stall.

### Citations

**File:** libraries/browser-extension-rpc/src/metadata.js (L50-78)
```javascript
const getIconData = (href) => {
  const img = new Image()

  img.crossOrigin = 'anonymous'
  img.src = href

  return new Promise((resolve) => {
    img.addEventListener('load', () => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      const dimensions = getIconDimensions(img, ICON_MAX_SIZE)

      const width = dimensions.width
      const height = dimensions.height

      canvas.width = width
      canvas.height = height

      ctx.drawImage(img, dimensions.dx, dimensions.dy, dimensions.dWidth, dimensions.dHeight)

      const { data } = ctx.getImageData(0, 0, width, height)

      resolve({ width, height, data: base64(data) })
    })

    // If can't compute, enable connecting dapp without icon. UI will render empty state
    img.onerror = () => resolve(null) // eslint-disable-line unicorn/prefer-add-event-listener
  })
}
```

**File:** libraries/browser-extension-rpc/src/metadata.js (L80-86)
```javascript
export const getIcon = async () => {
  const icons = document.querySelectorAll('head > link[rel~="icon"]')
  const sortedIcons = [...icons].sort((a, b) => getIconSize(b) - getIconSize(a))
  const href = sortedIcons[0]?.href || `${document.location.origin}/favicon.ico`

  return getIconData(href)
}
```

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
