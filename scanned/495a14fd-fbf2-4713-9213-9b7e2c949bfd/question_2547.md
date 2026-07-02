# Q2547: getAssetCurrentLimit Malformed Referral Payload Distribution Loop FeeReceiver P2547

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and supply very large or unusual referralId data on hot user flows, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to temporary freezing of funds? Probe condition: FeeReceiver reward route; amount case 0.01 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: supply very large or unusual referralId data on hot user flows; validation style: a helper contract batching allowed public calls; probe condition: FeeReceiver reward route; amount case 0.01 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the malformed referral payload path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: FeeReceiver reward route; amount case 0.01 ether; timing exactly at daily reset; caller model EOA caller.
