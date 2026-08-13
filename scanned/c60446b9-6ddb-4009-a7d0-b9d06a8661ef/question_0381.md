# Q381: metadata response mix-up via base64

## Question
Can an unprivileged attacker enter through dapp-controlled page metadata ingestion during wallet connect / approval UI rendering and control `name`, `port`, and `origin` so that `base64` in `libraries/browser-extension-rpc/src/metadata.js` make one origin reach a method namespace or capability that was only approved for another origin or flow, breaking the invariant that wallet-mutating or seed-ingesting methods must remain isolated from generic RPC capability exposure, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: libraries/browser-extension-rpc/src/metadata.js::base64
- Entrypoint: dapp-controlled page metadata ingestion during wallet connect / approval UI rendering
- Attacker controls: malformed JSON or RPC payload fields that still pass boundary parsing
- Exploit idea: make one origin reach a method namespace or capability that was only approved for another origin or flow
- Invariant to test: wallet-mutating or seed-ingesting methods must remain isolated from generic RPC capability exposure
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: fuzz malformed RPC payloads and verify the bridge rejects them before any wallet-mutating method is reached
