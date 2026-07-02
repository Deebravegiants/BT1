# Q3860: getAssetPrice Round Down Accumulation Zero Price Swell P3860

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, zero price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to temporary freezing of funds? Probe condition: Swell swETH legacy route; amount case 32.000001 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: Swell swETH legacy route; amount case 32.000001 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the round-down accumulation path against getAssetPrice and look for zero price breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, zero price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: mock zero/near-zero oracle values and assert no division path creates free assets or permanent freezes Use probe condition: Swell swETH legacy route; amount case 32.000001 ether; timing immediately after direct ETH donation; caller model EOA caller.
