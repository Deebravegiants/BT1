# Q31: depositETH Round Up Insolvency Rounding EigenLayer P0031

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to temporary freezing of funds? Probe condition: EigenLayer queued-withdrawal route; amount case 2 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: an attacker contract as msg.sender or recipient; probe condition: EigenLayer queued-withdrawal route; amount case 2 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the round-up insolvency path against depositETH and look for rounding breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: EigenLayer queued-withdrawal route; amount case 2 wei; timing same block before updateRSETHPrice; caller model EOA caller.
