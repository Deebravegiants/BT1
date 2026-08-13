# Q331: index response mix-up via createRpc

## Question
Can an unprivileged attacker enter through connected website RPC request handled by the wallet bridge and control `method`, `port`, and `name` so that `createRpc` in `libraries/browser-extension-rpc/src/index.js` make one origin reach a method namespace or capability that was only approved for another origin or flow, breaking the invariant that wallet-mutating or seed-ingesting methods must remain isolated from generic RPC capability exposure, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: libraries/browser-extension-rpc/src/index.js::createRpc
- Entrypoint: connected website RPC request handled by the wallet bridge
- Attacker controls: malformed JSON or RPC payload fields that still pass boundary parsing
- Exploit idea: make one origin reach a method namespace or capability that was only approved for another origin or flow
- Invariant to test: wallet-mutating or seed-ingesting methods must remain isolated from generic RPC capability exposure
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: drive a signing-capable request through the generic proxy path and assert it cannot import, mutate, or expose wallet secrets
