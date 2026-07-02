# Q178: depositETH Fee Mint Limit Boundary Fee Mint daily P0178

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to temporary freezing of funds? Probe condition: daily fee mint limit route; amount case 0.1 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: daily fee mint limit route; amount case 0.1 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the fee mint limit boundary path against depositETH and look for fee mint breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: daily fee mint limit route; amount case 0.1 ether; timing same block before updateRSETHPrice; caller model EOA caller.
