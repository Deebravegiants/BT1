# Q184: index RPC namespace confusion via factory

## Question
Can an unprivileged attacker enter through wallet-standard / browser-extension RPC method exposed to a connected website and control `port`, `port`, and `port` so that `factory` in `sdks/headless/src/features/wallet-rpc/index.js` rebind a response, subscription, or callback from one wallet session to another session, breaking the invariant that locked or unapproved state must not survive reconnect, proxy, or namespace confusion, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: sdks/headless/src/features/wallet-rpc/index.js::factory
- Entrypoint: wallet-standard / browser-extension RPC method exposed to a connected website
- Attacker controls: the RPC method path, nested arguments, wallet-account selector, and request timing
- Exploit idea: rebind a response, subscription, or callback from one wallet session to another session
- Invariant to test: locked or unapproved state must not survive reconnect, proxy, or namespace confusion
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: unit-test reconnect/disconnect races and assert no stale approval, unlock, or import state is reused
