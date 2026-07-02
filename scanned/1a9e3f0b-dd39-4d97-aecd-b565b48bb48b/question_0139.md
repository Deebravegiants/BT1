# Q139: depositETH FirstExcludedIndex Boundary Fee Mint Lido P0139

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: Lido stETH unstake route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: an attacker contract as msg.sender or recipient; probe condition: Lido stETH unstake route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the firstExcludedIndex boundary path against depositETH and look for fee mint breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: Lido stETH unstake route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller.
