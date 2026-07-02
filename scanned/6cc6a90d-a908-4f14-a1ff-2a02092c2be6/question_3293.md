# Q3293: getETHDistributionData Claim Replay Converter Desync Merkle-free P3293

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to temporary freezing of funds? Probe condition: Merkle-free yield accounting route; amount case minAmount plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: several attacker accounts creating adjacent requests; probe condition: Merkle-free yield accounting route; amount case minAmount plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the claim replay path against getETHDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: Merkle-free yield accounting route; amount case minAmount plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
