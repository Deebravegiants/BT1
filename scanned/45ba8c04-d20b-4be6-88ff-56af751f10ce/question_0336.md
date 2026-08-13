# Q336: index response mix-up via createUiRpc

## Question
Can an unprivileged attacker enter through connected website RPC request handled by the wallet bridge and control `name`, `method`, and `port` so that `createUiRpc` in `libraries/browser-extension-rpc/src/index.js` make one origin reach a method namespace or capability that was only approved for another origin or flow, breaking the invariant that wallet-mutating or seed-ingesting methods must remain isolated from generic RPC capability exposure, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: libraries/browser-extension-rpc/src/index.js::createUiRpc
- Entrypoint: connected website RPC request handled by the wallet bridge
- Attacker controls: malformed JSON or RPC payload fields that still pass boundary parsing
- Exploit idea: make one origin reach a method namespace or capability that was only approved for another origin or flow
- Invariant to test: wallet-mutating or seed-ingesting methods must remain isolated from generic RPC capability exposure
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: unit-test reconnect/disconnect races and assert no stale approval, unlock, or import state is reused
