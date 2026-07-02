# Q3291: getETHDistributionData Claim Replay eth Accounting EigenLayer P3291

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: EigenLayer queued-withdrawal route; amount case minAmount plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: a helper contract batching allowed public calls; probe condition: EigenLayer queued-withdrawal route; amount case minAmount plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the claim replay path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: EigenLayer queued-withdrawal route; amount case minAmount plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
