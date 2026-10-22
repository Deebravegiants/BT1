# [M] Arrakis V1 incident: On August 23, 2026, the Arrakis V1 / G-UNI ENS–WETH liquidity-manager vault (0x7c687f775a3b73bbab0e15832f24caab5d53bdde) was drain

## Summary
Severity: Medium
Target: Arrakis V1
Loss: $ 7,018
Attack method: Flashloan Price Manipulation
Published: 2026-08-23
Source: https://x.com/exvulsec/status/2091521539585999337
Type: slowmist-incident

## Details
On August 23, 2026, the Arrakis V1 / G-UNI ENS–WETH liquidity-manager vault (0x7c687f775a3b73bbab0e15832f24caab5d53bdde) was drained via Uniswap V3 spot-price manipulation. The attacker flash-loaned 1,800 WETH from Morpho Blue, skewed the pool’s instantaneous spot price, minted vault shares at the distorted valuation, restored the price, and burned the shares for a richer token mix, netting ≈2.94 WETH. Root cause: mint()/burn() valued the Uniswap V3 position off pool.slot0() with no TWAP or deviation guard (TWAP only protected rebalance()).
