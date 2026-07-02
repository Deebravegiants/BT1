# Q3656: updateRSETHPrice Buffer Under Reservation Highest Price queued P3656

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, highest price must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to protocol insolvency? Probe condition: queued buffer route; amount case minAmount minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: queued buffer route; amount case minAmount minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the buffer under-reservation path against updateRSETHPrice and look for highest price breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, highest price must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: queued buffer route; amount case minAmount minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
