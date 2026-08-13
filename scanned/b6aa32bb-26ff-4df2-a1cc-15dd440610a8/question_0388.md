# Q388: metadata proxy capability bleed via getTitle

## Question
Can an unprivileged attacker enter through dapp-controlled page metadata ingestion during wallet connect / approval UI rendering and control `icon`, `name`, and `port` so that `getTitle` in `libraries/browser-extension-rpc/src/metadata.js` confuse a seed-ingesting or wallet-mutating proxy into accepting attacker-controlled material in a read-mostly path, breaking the invariant that request IDs and callback routing must not let one website receive another website's wallet results, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: libraries/browser-extension-rpc/src/metadata.js::getTitle
- Entrypoint: dapp-controlled page metadata ingestion during wallet connect / approval UI rendering
- Attacker controls: a seed-bearing or signing-related payload routed through a generic RPC namespace
- Exploit idea: confuse a seed-ingesting or wallet-mutating proxy into accepting attacker-controlled material in a read-mostly path
- Invariant to test: request IDs and callback routing must not let one website receive another website's wallet results
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: unit-test reconnect/disconnect races and assert no stale approval, unlock, or import state is reused
