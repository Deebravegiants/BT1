# Q283: index proxy capability bleed via createRpc

## Question
Can an unprivileged attacker enter through connected website RPC request handled by the wallet bridge and control `method`, `port`, and `name` so that `createRpc` in `libraries/browser-extension-rpc/src/index.js` confuse a seed-ingesting or wallet-mutating proxy into accepting attacker-controlled material in a read-mostly path, breaking the invariant that request IDs and callback routing must not let one website receive another website's wallet results, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: libraries/browser-extension-rpc/src/index.js::createRpc
- Entrypoint: connected website RPC request handled by the wallet bridge
- Attacker controls: a seed-bearing or signing-related payload routed through a generic RPC namespace
- Exploit idea: confuse a seed-ingesting or wallet-mutating proxy into accepting attacker-controlled material in a read-mostly path
- Invariant to test: request IDs and callback routing must not let one website receive another website's wallet results
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: drive a signing-capable request through the generic proxy path and assert it cannot import, mutate, or expose wallet secrets
