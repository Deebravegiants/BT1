# Q3863: getAssetPrice Round Down Accumulation Stale Price ETHx P3863

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to permanent freezing of funds? Probe condition: ETHx supported asset route; amount case daily limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: a local supported-token harness with configurable transfer behavior; probe condition: ETHx supported asset route; amount case daily limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the round-down accumulation path against getAssetPrice and look for stale price breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: sequence price update/deposit/withdraw with stale and fresh prices and assert no profitable round trip. Use probe condition: ETHx supported asset route; amount case daily limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
