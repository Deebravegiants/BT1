# Q2554: getAssetCurrentLimit Malformed Referral Payload Rounding deposit-limit P2554

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and supply very large or unusual referralId data on hot user flows, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: deposit-limit accounting route; amount case 0.01 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: supply very large or unusual referralId data on hot user flows; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: deposit-limit accounting route; amount case 0.01 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the malformed referral payload path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: deposit-limit accounting route; amount case 0.01 ether; timing exactly at daily reset; caller model EOA caller.
