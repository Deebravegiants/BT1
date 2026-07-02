# Q6: depositETH Stale Price Sandwich Fee Mint LRTOracle P0006

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that asset value and rsETH supply move consistently across the two legs; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to direct theft of user funds? Probe condition: LRTOracle price route; amount case 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices; validation style: compare many dust calls against one large call; probe condition: LRTOracle price route; amount case 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the stale-price sandwich path against depositETH and look for fee mint breaking value conservation or liveness.
- Invariant to test: asset value and rsETH supply move consistently across the two legs; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: LRTOracle price route; amount case 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
