# Q459: rpc RPC namespace confusion via RPC

## Question
Can an unprivileged attacker enter through connected website RPC request handled by the wallet bridge and control `origin`, `name`, and `method` so that `RPC` in `libraries/sdk-rpc/src/rpc.ts` rebind a response, subscription, or callback from one wallet session to another session, breaking the invariant that locked or unapproved state must not survive reconnect, proxy, or namespace confusion, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: libraries/sdk-rpc/src/rpc.ts::RPC
- Entrypoint: connected website RPC request handled by the wallet bridge
- Attacker controls: the RPC method path, nested arguments, wallet-account selector, and request timing
- Exploit idea: rebind a response, subscription, or callback from one wallet session to another session
- Invariant to test: locked or unapproved state must not survive reconnect, proxy, or namespace confusion
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: unit-test reconnect/disconnect races and assert no stale approval, unlock, or import state is reused
