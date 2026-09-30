# [M] Lack of slippage and deadline protection in deposit

## Summary
Severity: Medium
Contest weight: 0.2008
Dataset id: 2348
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
1. When users [deposit](https://github.com/code-423n4/2025-03-silo-finance/blob/main/silo-vaults/contracts/SiloVault.sol#L569) funds, those assets are allocated to one or more underlying ERC4626 markets according to the supply queue.
2. When withdrawing or redeeming, assets are pulled from the underlying markets according to the withdraw queue and shares burned.

None of these actions allow the user to specify any acceptable slippage or deadline.

  * The vault interacts with multiple ERC4626 vaults. Share price in these underlying vaults can change between transaction submission and execution.
  * During deposit, the protocol might need to distribute assets across multiple markets based on their caps. This multi-step process could expose users to price changes.
  * During withdrawals or redemptions, the protocol attempts to pull assets from markets in a specific order. If a market has insufficient liquidity, the next market is tried, which might have different share pricing.
  * The [_accrueFee()](https://github.com/code-423n4/2025-03-silo-finance/blob/main/silo-vaults/contracts/SiloVault.sol#L942) function is called during both deposit and withdrawal, which can change the conversion rate between shares and assets.

Additionally, there’s a risk of transactions getting stuck in the mempool during periods of network congestion and hence deadline protection is needed.

User may recieve less than expected shares or assets due to unfavourable price movement or execution delays.

## Recommendation
Allow the user to specify paramaters like `minShares`, `minAssets` while calling these functions.

IhorSF (Silo Finance) disputed
