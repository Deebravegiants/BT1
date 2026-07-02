# Q225: depositETH Claim Replay Rounding rsETH P0225

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: rsETH transfer route; amount case 32 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: rsETH transfer route; amount case 32 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the claim replay path against depositETH and look for rounding breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: rsETH transfer route; amount case 32 ether; timing same block before updateRSETHPrice; caller model EOA caller.
