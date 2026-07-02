# Q3194: getETHDistributionData Nonce Collision Attempt Price Update deposit-limit P3194

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to failure to deliver promised returns without principal loss? Probe condition: deposit-limit accounting route; amount case deposit limit plus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: two transactions before and after updateRSETHPrice; probe condition: deposit-limit accounting route; amount case deposit limit plus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the nonce collision attempt path against getETHDistributionData and look for price update breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: deposit-limit accounting route; amount case deposit limit plus 1 wei; timing one second after daily reset; caller model EOA caller.
