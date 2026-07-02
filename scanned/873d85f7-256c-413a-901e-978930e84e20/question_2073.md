# Q2073: getRsETHAmountToMint Oracle Decimal Mismatch Mint Rate Merkle-free P2073

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: Merkle-free yield accounting route; amount case exact minAmount; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: Merkle-free yield accounting route; amount case exact minAmount; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the oracle decimal mismatch path against getRsETHAmountToMint and look for mint rate breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: Merkle-free yield accounting route; amount case exact minAmount; timing one second before daily reset; caller model EOA caller.
