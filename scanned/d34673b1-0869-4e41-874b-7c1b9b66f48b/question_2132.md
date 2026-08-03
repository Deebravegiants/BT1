# Q2132: set_accept_ownership can create underpriced public NFT work

## Question
Can an unprivileged attacker abuse `set_accept_ownership` with crafted call repetition, batching order, and surrounding state to force underpriced scans, cleanup, or attribute processing over `Collection` / `Asset`, degrading block production?

## Target
- File/function: substrate/frame/uniques/src/lib.rs::set_accept_ownership
- Entrypoint: signed extrinsic `set_accept_ownership`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Look for public loops over items, attributes, approvals, or swap lists whose true cost grows faster than charged weight.
- Invariant to test: The public worst-case cost must remain within charged weight and must not expose a griefing path to persistent slowdown.
- Expected Immunefi impact: Permanent asset lock or state corruption that blocks transfers
- Fast validation: Fuzz maximal metadata, approvals, attributes, and item vectors; compare actual execution cost to benchmark assumptions.
