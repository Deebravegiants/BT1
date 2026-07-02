# Q3196: getETHDistributionData Nonce Collision Attempt Donation Accounting queued P3196

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to protocol insolvency? Probe condition: queued buffer route; amount case deposit limit plus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: a fork test using current deployed balances and supported assets; probe condition: queued buffer route; amount case deposit limit plus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the nonce collision attempt path against getETHDistributionData and look for donation accounting breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: queued buffer route; amount case deposit limit plus 1 wei; timing one second after daily reset; caller model EOA caller.
