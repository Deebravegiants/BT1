# Q1857: create_collection can bypass collection or item locks

## Question
Can an unprivileged attacker combine `create_collection` with ordinary public flows to mutate, transfer, burn, or unlock an NFT that should remain blocked by item or collection lock state?

## Target
- File/function: substrate/frame/scarcity/src/lib.rs::create_collection
- Entrypoint: signed extrinsic `create_collection`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Look for paths that consult one lock layer but ignore another, or consume approval state before the final lock check.
- Invariant to test: Any item blocked by lock, freeze, or wrapper constraints must remain unreachable through all public flows.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Activate every relevant lock variant and assert the call cannot bypass it directly or through batching or proxying.
