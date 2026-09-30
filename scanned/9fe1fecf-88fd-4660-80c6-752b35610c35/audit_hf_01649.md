# [M] Unbounded storage iteration in EVM address registration migration

## Summary
Severity: Medium
Contest weight: 0.1175
Dataset id: 8847
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SetCodeForErc20Precompile::on_runtime_upgrade() performs an unbounded iteration over all assets in the registry to register their EVM addresses. This approach poses several risks:
- Block Space Exhaustion: with a large number of assets (>1000), the migration could exceed block weight limits, causing the upgrade to fail.
- Network Disruption: A failed upgrade due to exceeded block limits would require network coordination to resolve, potentially leading to downtime.
fn on_runtime_upgrade() -> frame_support::weights::Weight {
    pallet_asset_registry::Assets::<Runtime>::iter().for_each(|(asset_id, _)| {
        // ... processing each asset in a single block
    });
}
References: link

## Recommendation
Implement a scheduled multi-block migration using the Scheduler pallet:
- Define migration state storage
- Process assets in configurable batches (e.g., 100 per block)
- Use the Scheduler pallet to ensure consistent execution
- Track progress for migration resumption
