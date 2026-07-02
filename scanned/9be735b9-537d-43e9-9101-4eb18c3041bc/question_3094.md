# Q3094: getETHDistributionData Round Down Accumulation Converter Desync deposit-limit P3094

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to temporary freezing of funds? Probe condition: deposit-limit accounting route; amount case daily limit exactly; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: deposit-limit accounting route; amount case daily limit exactly; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the round-down accumulation path against getETHDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: deposit-limit accounting route; amount case daily limit exactly; timing one second after daily reset; caller model EOA caller.
