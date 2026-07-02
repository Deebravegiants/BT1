# Q3935: getAssetPrice Reentrant Token Callback Decimals withdrawal P3935

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, decimals must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to protocol insolvency? Probe condition: withdrawal request nonce route; amount case available liquidity exactly; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path; validation style: a local supported-token harness with configurable transfer behavior; probe condition: withdrawal request nonce route; amount case available liquidity exactly; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the reentrant token callback path against getAssetPrice and look for decimals breaking value conservation or liveness.
- Invariant to test: nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, decimals must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: fuzz oracle precision and token decimals assumptions and assert 1e18 normalization is consistent Use probe condition: withdrawal request nonce route; amount case available liquidity exactly; timing immediately after direct ETH donation; caller model EOA caller.
