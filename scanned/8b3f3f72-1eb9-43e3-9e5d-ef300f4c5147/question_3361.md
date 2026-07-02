# Q3361: getETHDistributionData Allowance Race eth Accounting ETH P3361

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: ETH sentinel route; amount case 0.1 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: one transaction using a contract wallet and controlled calldata; probe condition: ETH sentinel route; amount case 0.1 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use single transaction to exercise the allowance race path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: ETH sentinel route; amount case 0.1 ether; timing immediately after reward sendFunds; caller model EOA caller.
