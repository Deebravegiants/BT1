# Q2527: getAssetCurrentLimit Claim Replay Deposit Limit FeeReceiver P2527

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: FeeReceiver reward route; amount case 0.001 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: an attacker contract as msg.sender or recipient; probe condition: FeeReceiver reward route; amount case 0.001 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the claim replay path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: FeeReceiver reward route; amount case 0.001 ether; timing exactly at daily reset; caller model EOA caller.
