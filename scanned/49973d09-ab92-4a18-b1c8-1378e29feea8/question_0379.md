# Q379: metadata RPC namespace confusion via getIconData

## Question
Can an unprivileged attacker enter through dapp-controlled page metadata ingestion during wallet connect / approval UI rendering and control `origin`, `icon`, and `name` so that `getIconData` in `libraries/browser-extension-rpc/src/metadata.js` rebind a response, subscription, or callback from one wallet session to another session, breaking the invariant that locked or unapproved state must not survive reconnect, proxy, or namespace confusion, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: libraries/browser-extension-rpc/src/metadata.js::getIconData
- Entrypoint: dapp-controlled page metadata ingestion during wallet connect / approval UI rendering
- Attacker controls: the RPC method path, nested arguments, wallet-account selector, and request timing
- Exploit idea: rebind a response, subscription, or callback from one wallet session to another session
- Invariant to test: locked or unapproved state must not survive reconnect, proxy, or namespace confusion
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: drive a signing-capable request through the generic proxy path and assert it cannot import, mutate, or expose wallet secrets
