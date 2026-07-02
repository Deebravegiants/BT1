# Q45: depositETH Zero Or Dust Edge Fee Mint rsETH P0045

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: rsETH transfer route; amount case minAmount minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: rsETH transfer route; amount case minAmount minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the zero-or-dust edge path against depositETH and look for fee mint breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: rsETH transfer route; amount case minAmount minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
