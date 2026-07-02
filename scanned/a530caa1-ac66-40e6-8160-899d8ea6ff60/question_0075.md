# Q75: depositETH Rebasing Balance Drift Rounding withdrawal P0075

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and let a supported rebasing LST balance change between request creation and final settlement, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to temporary freezing of funds? Probe condition: withdrawal request nonce route; amount case exact minAmount; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: let a supported rebasing LST balance change between request creation and final settlement; validation style: a helper contract batching allowed public calls; probe condition: withdrawal request nonce route; amount case exact minAmount; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the rebasing balance drift path against depositETH and look for rounding breaking value conservation or liveness.
- Invariant to test: rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: withdrawal request nonce route; amount case exact minAmount; timing same block before updateRSETHPrice; caller model EOA caller.
