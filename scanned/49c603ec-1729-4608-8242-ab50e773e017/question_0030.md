# Q30: depositETH Round Up Insolvency Deposit Limit NodeDelegator P0030

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: NodeDelegator pod-share route; amount case 2 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: compare many dust calls against one large call; probe condition: NodeDelegator pod-share route; amount case 2 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the round-up insolvency path against depositETH and look for deposit limit breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: NodeDelegator pod-share route; amount case 2 wei; timing same block before updateRSETHPrice; caller model EOA caller.
