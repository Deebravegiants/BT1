# Q1538: receiveFromNodeDelegator Stale Price Sandwich Price Update daily P1538

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that asset value and rsETH supply move consistently across the two legs; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: daily fee mint limit route; amount case available liquidity exactly; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices; validation style: two transactions before and after updateRSETHPrice; probe condition: daily fee mint limit route; amount case available liquidity exactly; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the stale-price sandwich path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: asset value and rsETH supply move consistently across the two legs; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: daily fee mint limit route; amount case available liquidity exactly; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
