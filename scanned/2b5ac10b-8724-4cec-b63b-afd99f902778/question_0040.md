# Q40: depositETH Zero Or Dust Edge Mint Rate Swell P0040

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: Swell swETH legacy route; amount case 2 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: a fork test using current deployed balances and supported assets; probe condition: Swell swETH legacy route; amount case 2 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the zero-or-dust edge path against depositETH and look for mint rate breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: Swell swETH legacy route; amount case 2 wei; timing same block before updateRSETHPrice; caller model EOA caller.
