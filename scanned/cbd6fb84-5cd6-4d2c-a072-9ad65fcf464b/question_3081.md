# Q3081: getETHDistributionData Stale Price Sandwich eth Accounting ETH P3081

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that asset value and rsETH supply move consistently across the two legs; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: ETH sentinel route; amount case daily limit exactly; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: ETH sentinel route; amount case daily limit exactly; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the stale-price sandwich path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: asset value and rsETH supply move consistently across the two legs; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: ETH sentinel route; amount case daily limit exactly; timing one second after daily reset; caller model EOA caller.
