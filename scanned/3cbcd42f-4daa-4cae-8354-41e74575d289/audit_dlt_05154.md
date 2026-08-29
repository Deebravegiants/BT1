# [?] fix emission gate underflow stranding block emission

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-07-27
Source: https://github.com/RaoFoundation/subtensor/commit/7e20eb76c0a9d1068d7d6e536c73a6eedcc06e90
Type: security-commit

## Details
fix emission gate underflow stranding block emission

When a stale theta and steep h drive every gated share to zero in
fixed-point, restore the ungated distribution so get_subnet_block_emissions
cannot emit zero everywhere. Cover with the 256-equal / h=8 boundary case.

Co-authored-by: Cursor <cursoragent@cursor.com>
