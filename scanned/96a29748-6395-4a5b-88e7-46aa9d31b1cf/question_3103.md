# Q3103: getETHDistributionData Round Up Insolvency eth Accounting ETHx P3103

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: ETHx supported asset route; amount case available liquidity minus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: an attacker contract as msg.sender or recipient; probe condition: ETHx supported asset route; amount case available liquidity minus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the round-up insolvency path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: ETHx supported asset route; amount case available liquidity minus 1 wei; timing one second after daily reset; caller model EOA caller.
