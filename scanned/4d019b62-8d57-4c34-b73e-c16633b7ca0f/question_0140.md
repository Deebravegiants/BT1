# Q140: depositETH FirstExcludedIndex Boundary Mint Rate Swell P0140

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to temporary freezing of funds? Probe condition: Swell swETH legacy route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: Swell swETH legacy route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the firstExcludedIndex boundary path against depositETH and look for mint rate breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: Swell swETH legacy route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller.
