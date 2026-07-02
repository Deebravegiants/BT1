# Q3859: getAssetPrice Round Down Accumulation Decimals Lido P3859

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, decimals must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to protocol insolvency? Probe condition: Lido stETH unstake route; amount case 32.000001 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: an attacker contract as msg.sender or recipient; probe condition: Lido stETH unstake route; amount case 32.000001 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the round-down accumulation path against getAssetPrice and look for decimals breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, decimals must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: fuzz oracle precision and token decimals assumptions and assert 1e18 normalization is consistent Use probe condition: Lido stETH unstake route; amount case 32.000001 ether; timing immediately after direct ETH donation; caller model EOA caller.
