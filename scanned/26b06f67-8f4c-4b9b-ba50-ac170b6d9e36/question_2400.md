# Q2400: getAssetCurrentLimit Reentrant Token Callback Distribution Loop Swell P2400

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to temporary freezing of funds? Probe condition: Swell swETH legacy route; amount case deposit limit plus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path; validation style: attacker-created state followed by an honest operator action; probe condition: Swell swETH legacy route; amount case deposit limit plus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the reentrant token callback path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: Swell swETH legacy route; amount case deposit limit plus 1 wei; timing one second before daily reset; caller model EOA caller.
