# Q2532: getAssetCurrentLimit Claim Replay Rounding Aave P2532

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: Aave aWETH liquidity route; amount case 0.001 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: attacker-created state followed by an honest operator action; probe condition: Aave aWETH liquidity route; amount case 0.001 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the claim replay path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: Aave aWETH liquidity route; amount case 0.001 ether; timing exactly at daily reset; caller model EOA caller.
