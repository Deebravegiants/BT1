# Q2081: clear_collection_metadata can create underpriced public NFT work

## Question
Can an unprivileged attacker abuse `clear_collection_metadata` with crafted IDs, hashes, nonces, or location fields to force underpriced scans, cleanup, or attribute processing over `Collection` / `Item`, degrading block production?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::clear_collection_metadata
- Entrypoint: signed extrinsic `clear_collection_metadata`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Look for public loops over items, attributes, approvals, or swap lists whose true cost grows faster than charged weight.
- Invariant to test: The public worst-case cost must remain within charged weight and must not expose a griefing path to persistent slowdown.
- Expected Immunefi impact: Permanent asset lock or state corruption that blocks transfers
- Fast validation: Fuzz maximal metadata, approvals, attributes, and item vectors; compare actual execution cost to benchmark assumptions.
