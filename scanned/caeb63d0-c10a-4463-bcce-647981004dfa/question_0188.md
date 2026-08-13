# Q188: index proxy capability bleed via walletRpc

## Question
Can an unprivileged attacker enter through wallet-standard / browser-extension RPC method exposed to a connected website and control `port`, `port`, and `port` so that `walletRpc` in `sdks/headless/src/features/wallet-rpc/index.js` confuse a seed-ingesting or wallet-mutating proxy into accepting attacker-controlled material in a read-mostly path, breaking the invariant that request IDs and callback routing must not let one website receive another website's wallet results, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: sdks/headless/src/features/wallet-rpc/index.js::walletRpc
- Entrypoint: wallet-standard / browser-extension RPC method exposed to a connected website
- Attacker controls: a seed-bearing or signing-related payload routed through a generic RPC namespace
- Exploit idea: confuse a seed-ingesting or wallet-mutating proxy into accepting attacker-controlled material in a read-mostly path
- Invariant to test: request IDs and callback routing must not let one website receive another website's wallet results
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: unit-test reconnect/disconnect races and assert no stale approval, unlock, or import state is reused
