# Q3290: getETHDistributionData Claim Replay Price Update NodeDelegator P3290

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to failure to deliver promised returns without principal loss? Probe condition: NodeDelegator pod-share route; amount case minAmount plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: two transactions before and after updateRSETHPrice; probe condition: NodeDelegator pod-share route; amount case minAmount plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the claim replay path against getETHDistributionData and look for price update breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: NodeDelegator pod-share route; amount case minAmount plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
