# Q2659: getAssetCurrentLimit Committed Assets Desync Distribution Loop Lido P2659

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to block stuffing? Probe condition: Lido stETH unstake route; amount case 32.000001 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: an attacker contract as msg.sender or recipient; probe condition: Lido stETH unstake route; amount case 32.000001 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the committed-assets desync path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: Lido stETH unstake route; amount case 32.000001 ether; timing exactly at daily reset; caller model EOA caller.
