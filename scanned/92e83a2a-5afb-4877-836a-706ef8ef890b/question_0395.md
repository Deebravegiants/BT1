# Q395: metadata stale session reuse via getIconSize

## Question
Can an unprivileged attacker enter through dapp-controlled page metadata ingestion during wallet connect / approval UI rendering and control `origin`, `icon`, and `name` so that `getIconSize` in `libraries/browser-extension-rpc/src/metadata.js` make malformed input fail open and select a dangerous default path instead of being rejected, breaking the invariant that origin/session bindings must remain one-to-one across RPC requests, responses, and subscriptions, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: libraries/browser-extension-rpc/src/metadata.js::getIconSize
- Entrypoint: dapp-controlled page metadata ingestion during wallet connect / approval UI rendering
- Attacker controls: two concurrent port sessions, reused request IDs, and response ordering
- Exploit idea: make malformed input fail open and select a dangerous default path instead of being rejected
- Invariant to test: origin/session bindings must remain one-to-one across RPC requests, responses, and subscriptions
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: drive a signing-capable request through the generic proxy path and assert it cannot import, mutate, or expose wallet secrets
