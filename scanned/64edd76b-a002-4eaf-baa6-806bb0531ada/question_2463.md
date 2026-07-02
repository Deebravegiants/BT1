# Q2463: getAssetCurrentLimit Highest Price Ratchet Distribution Loop ETHx P2463

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to block stuffing? Probe condition: ETHx supported asset route; amount case exact minAmount; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: a helper contract batching allowed public calls; probe condition: ETHx supported asset route; amount case exact minAmount; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the highest-price ratchet path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: ETHx supported asset route; amount case exact minAmount; timing exactly at daily reset; caller model EOA caller.
