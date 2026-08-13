# Q1546: seed metadata fail-open bridge parsing via createPrimarySeedMetadata

## Question
Can an unprivileged attacker enter through dapp-controlled page metadata ingestion during wallet connect / approval UI rendering and control `name`, `port`, and `name` so that `createPrimarySeedMetadata` in `features/wallet/migrations/seed-metadata.js` carry pre-approval, unlocked, or imported-seed state across a boundary that should reset it, breaking the invariant that malformed RPC payloads must fail closed and never select state-changing defaults, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: features/wallet/migrations/seed-metadata.js::createPrimarySeedMetadata
- Entrypoint: dapp-controlled page metadata ingestion during wallet connect / approval UI rendering
- Attacker controls: a metadata-bearing request plus disconnect/reconnect timing from the same browser session
- Exploit idea: carry pre-approval, unlocked, or imported-seed state across a boundary that should reset it
- Invariant to test: malformed RPC payloads must fail closed and never select state-changing defaults
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: drive a signing-capable request through the generic proxy path and assert it cannot import, mutate, or expose wallet secrets
