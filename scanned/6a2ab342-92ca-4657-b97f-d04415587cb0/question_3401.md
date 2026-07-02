# Q3401: getETHDistributionData Unexpected Receiver Revert Price Update ETH P3401

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to failure to deliver promised returns without principal loss? Probe condition: ETH sentinel route; amount case 31.999999 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: several attacker accounts creating adjacent requests; probe condition: ETH sentinel route; amount case 31.999999 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the unexpected receiver revert path against getETHDistributionData and look for price update breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: ETH sentinel route; amount case 31.999999 ether; timing immediately after reward sendFunds; caller model EOA caller.
