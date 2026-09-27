# [M] Potentially Stale Adapter Mapping in `totalValueInDStable`

## Summary
Severity: Medium
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-16
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/25
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/tre)

  **Beneficiary:** 0x4C97Aa53fffF60dF05626aa1455418AF43F564e4
  **Submission hash (on-chain):** 0x09d7e3b0314f7dcc877c79e3c4d9855e8c6eec0108c63014970a131c3227c659
  **Severity:** medium
  
  **Description:**
  **Description**\
`totalValueInDStable` derives each asset’s adapter from the router every call:

```solidity
address adapterAddress = IAdapterProvider(router)
        .vaultAssetToAdapter(vaultAsset);
```

If governance removes or replaces an adapter in the router but forgets to update the vault’s _supportedAssets, the loop will silently skip that asset (adapter address =0) or use an outdated adapter, producing an incorrect TVL.

**Recommendation**\

- Emit an event whenever `vaultAssetToAdapter` is changed.

- Add a periodic or on-demand sanity-check that every `_supportedAsset` has a non-zero adapter.

- Optionally, revert if `adapterAddress == address(0)` instead of skipping.
