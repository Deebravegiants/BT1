# Q364: metadata RPC namespace confusion via getTitle

## Question
Can an unprivileged attacker enter through dapp-controlled page metadata ingestion during wallet connect / approval UI rendering and control `icon`, `name`, and `port` so that `getTitle` in `libraries/browser-extension-rpc/src/metadata.js` rebind a response, subscription, or callback from one wallet session to another session, breaking the invariant that locked or unapproved state must not survive reconnect, proxy, or namespace confusion, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: libraries/browser-extension-rpc/src/metadata.js::getTitle
- Entrypoint: dapp-controlled page metadata ingestion during wallet connect / approval UI rendering
- Attacker controls: the RPC method path, nested arguments, wallet-account selector, and request timing
- Exploit idea: rebind a response, subscription, or callback from one wallet session to another session
- Invariant to test: locked or unapproved state must not survive reconnect, proxy, or namespace confusion
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: unit-test reconnect/disconnect races and assert no stale approval, unlock, or import state is reused
