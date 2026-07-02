# Q2391: getAssetCurrentLimit Reentrant Token Callback Rounding EigenLayer P2391

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: EigenLayer queued-withdrawal route; amount case deposit limit plus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path; validation style: a helper contract batching allowed public calls; probe condition: EigenLayer queued-withdrawal route; amount case deposit limit plus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the reentrant token callback path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: EigenLayer queued-withdrawal route; amount case deposit limit plus 1 wei; timing one second before daily reset; caller model EOA caller.
