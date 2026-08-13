# Q187: index fail-open bridge parsing via factory

## Question
Can an unprivileged attacker enter through wallet-standard / browser-extension RPC method exposed to a connected website and control `port`, `port`, and `port` so that `factory` in `sdks/headless/src/features/wallet-rpc/index.js` carry pre-approval, unlocked, or imported-seed state across a boundary that should reset it, breaking the invariant that malformed RPC payloads must fail closed and never select state-changing defaults, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: sdks/headless/src/features/wallet-rpc/index.js::factory
- Entrypoint: wallet-standard / browser-extension RPC method exposed to a connected website
- Attacker controls: a metadata-bearing request plus disconnect/reconnect timing from the same browser session
- Exploit idea: carry pre-approval, unlocked, or imported-seed state across a boundary that should reset it
- Invariant to test: malformed RPC payloads must fail closed and never select state-changing defaults
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: drive a signing-capable request through the generic proxy path and assert it cannot import, mutate, or expose wallet secrets
