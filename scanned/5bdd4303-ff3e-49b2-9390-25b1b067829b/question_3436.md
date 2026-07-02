# Q3436: getETHDistributionData Unclaimed Yield Diversion Donation Accounting queued P3436

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to protocol insolvency? Probe condition: queued buffer route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: a fork test using current deployed balances and supported assets; probe condition: queued buffer route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the unclaimed-yield diversion path against getETHDistributionData and look for donation accounting breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: queued buffer route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller.
