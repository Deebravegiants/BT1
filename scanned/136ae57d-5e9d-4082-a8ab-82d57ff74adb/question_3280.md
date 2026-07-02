# Q3280: getETHDistributionData Buffer Over Reservation eth Accounting Swell P3280

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: Swell swETH legacy route; amount case exact minAmount; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: a fork test using current deployed balances and supported assets; probe condition: Swell swETH legacy route; amount case exact minAmount; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the buffer over-reservation path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: Swell swETH legacy route; amount case exact minAmount; timing immediately after reward sendFunds; caller model EOA caller.
