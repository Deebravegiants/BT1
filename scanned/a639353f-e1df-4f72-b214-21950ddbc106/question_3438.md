# Q3438: getETHDistributionData Unclaimed Yield Diversion Price Update daily P3438

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to failure to deliver promised returns without principal loss? Probe condition: daily fee mint limit route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: compare many dust calls against one large call; probe condition: daily fee mint limit route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the unclaimed-yield diversion path against getETHDistributionData and look for price update breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: daily fee mint limit route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller.
