# Q219: depositETH Claim Replay Rounding Lido P0219

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to direct theft of user funds? Probe condition: Lido stETH unstake route; amount case 31.999999 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: a helper contract batching allowed public calls; probe condition: Lido stETH unstake route; amount case 31.999999 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the claim replay path against depositETH and look for rounding breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: Lido stETH unstake route; amount case 31.999999 ether; timing same block before updateRSETHPrice; caller model EOA caller.
