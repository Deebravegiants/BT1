# Q370: metadata stale session reuse via getTitle

## Question
Can an unprivileged attacker enter through dapp-controlled page metadata ingestion during wallet connect / approval UI rendering and control `port`, `origin`, and `icon` so that `getTitle` in `libraries/browser-extension-rpc/src/metadata.js` make malformed input fail open and select a dangerous default path instead of being rejected, breaking the invariant that origin/session bindings must remain one-to-one across RPC requests, responses, and subscriptions, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: libraries/browser-extension-rpc/src/metadata.js::getTitle
- Entrypoint: dapp-controlled page metadata ingestion during wallet connect / approval UI rendering
- Attacker controls: two concurrent port sessions, reused request IDs, and response ordering
- Exploit idea: make malformed input fail open and select a dangerous default path instead of being rejected
- Invariant to test: origin/session bindings must remain one-to-one across RPC requests, responses, and subscriptions
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: simulate two origins or port sessions, interleave requests and responses, and assert that only the approved origin receives the intended result
