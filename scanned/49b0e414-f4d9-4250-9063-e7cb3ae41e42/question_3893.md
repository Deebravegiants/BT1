# Q3893: getAssetPrice Direct ETH Donation Skew Zero Price Merkle-free P3893

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, zero price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to temporary freezing of funds? Probe condition: Merkle-free yield accounting route; amount case daily limit exactly; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: several attacker accounts creating adjacent requests; probe condition: Merkle-free yield accounting route; amount case daily limit exactly; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the direct ETH donation skew path against getAssetPrice and look for zero price breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, zero price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: mock zero/near-zero oracle values and assert no division path creates free assets or permanent freezes Use probe condition: Merkle-free yield accounting route; amount case daily limit exactly; timing immediately after direct ETH donation; caller model EOA caller.
