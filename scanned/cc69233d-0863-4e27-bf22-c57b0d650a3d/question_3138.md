# Q3138: getETHDistributionData Fee On Transfer Token Skew Converter Desync daily P3138

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to temporary freezing of funds? Probe condition: daily fee mint limit route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: compare many dust calls against one large call; probe condition: daily fee mint limit route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the fee-on-transfer token skew path against getETHDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: daily fee mint limit route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller.
