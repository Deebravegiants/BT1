# Q3136: getETHDistributionData Fee On Transfer Token Skew eth Accounting queued P3136

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: queued buffer route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: a fork test using current deployed balances and supported assets; probe condition: queued buffer route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the fee-on-transfer token skew path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: queued buffer route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller.
