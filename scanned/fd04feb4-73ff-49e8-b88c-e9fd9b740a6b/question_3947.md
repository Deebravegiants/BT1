# Q3947: getAssetPrice Pause Boundary Race Zero Price FeeReceiver P3947

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, zero price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to temporary freezing of funds? Probe condition: FeeReceiver reward route; amount case available liquidity plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: race a public action around a pause or public price-triggered pause transition; validation style: a local supported-token harness with configurable transfer behavior; probe condition: FeeReceiver reward route; amount case available liquidity plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the pause boundary race path against getAssetPrice and look for zero price breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, zero price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: mock zero/near-zero oracle values and assert no division path creates free assets or permanent freezes Use probe condition: FeeReceiver reward route; amount case available liquidity plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
