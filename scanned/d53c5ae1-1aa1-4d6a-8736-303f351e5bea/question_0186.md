# Q186: index response mix-up via createSeedIngestingProxy

## Question
Can an unprivileged attacker enter through wallet-standard / browser-extension RPC method exposed to a connected website and control `port`, `port`, and `port` so that `createSeedIngestingProxy` in `sdks/headless/src/features/wallet-rpc/index.js` make one origin reach a method namespace or capability that was only approved for another origin or flow, breaking the invariant that wallet-mutating or seed-ingesting methods must remain isolated from generic RPC capability exposure, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: sdks/headless/src/features/wallet-rpc/index.js::createSeedIngestingProxy
- Entrypoint: wallet-standard / browser-extension RPC method exposed to a connected website
- Attacker controls: malformed JSON or RPC payload fields that still pass boundary parsing
- Exploit idea: make one origin reach a method namespace or capability that was only approved for another origin or flow
- Invariant to test: wallet-mutating or seed-ingesting methods must remain isolated from generic RPC capability exposure
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: simulate two origins or port sessions, interleave requests and responses, and assert that only the approved origin receives the intended result
