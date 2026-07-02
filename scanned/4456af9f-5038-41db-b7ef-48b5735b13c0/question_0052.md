# Q52: depositETH Direct ETH Donation Skew Deposit Limit Aave P0052

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: Aave aWETH liquidity route; amount case minAmount minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: a fork test using current deployed balances and supported assets; probe condition: Aave aWETH liquidity route; amount case minAmount minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the direct ETH donation skew path against depositETH and look for deposit limit breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: Aave aWETH liquidity route; amount case minAmount minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
