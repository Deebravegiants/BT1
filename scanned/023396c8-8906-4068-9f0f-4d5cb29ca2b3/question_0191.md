# Q191: depositETH Aave Liquidity Shortfall Deposit Limit EigenLayer P0191

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to direct theft of user funds? Probe condition: EigenLayer queued-withdrawal route; amount case 1 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal; validation style: a local supported-token harness with configurable transfer behavior; probe condition: EigenLayer queued-withdrawal route; amount case 1 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the Aave liquidity shortfall path against depositETH and look for deposit limit breaking value conservation or liveness.
- Invariant to test: external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: EigenLayer queued-withdrawal route; amount case 1 ether; timing same block before updateRSETHPrice; caller model EOA caller.
