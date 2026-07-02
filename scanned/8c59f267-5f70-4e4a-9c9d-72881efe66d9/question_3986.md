# Q3986: getAssetPrice Oracle Decimal Mismatch Zero Price LRTOracle P3986

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, zero price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to temporary freezing of funds? Probe condition: LRTOracle price route; amount case deposit limit plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: two transactions before and after updateRSETHPrice; probe condition: LRTOracle price route; amount case deposit limit plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the oracle decimal mismatch path against getAssetPrice and look for zero price breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, zero price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: mock zero/near-zero oracle values and assert no division path creates free assets or permanent freezes Use probe condition: LRTOracle price route; amount case deposit limit plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
