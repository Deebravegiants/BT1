# [?] Ignore RUSTSEC-2026-0258 until the fork tree leaves h2 0.3.

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-08-18
Source: https://github.com/RaoFoundation/subtensor/commit/00a05e9381f3594d1d57310291eb1529ee7b6d5e
Type: security-commit

## Details
Ignore RUSTSEC-2026-0258 until the fork tree leaves h2 0.3.

The new h2 empty-DATA advisory only has a 0.4.16 fix; 0.3.27 has no patch and is still pulled in by hyper in the polkadot-sdk stack.

Co-authored-by: Cursor <cursoragent@cursor.com>
