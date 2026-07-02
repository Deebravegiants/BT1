# Q3435: getETHDistributionData Unclaimed Yield Diversion eth Accounting withdrawal P3435

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: withdrawal request nonce route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: a helper contract batching allowed public calls; probe condition: withdrawal request nonce route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the unclaimed-yield diversion path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: withdrawal request nonce route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller.
