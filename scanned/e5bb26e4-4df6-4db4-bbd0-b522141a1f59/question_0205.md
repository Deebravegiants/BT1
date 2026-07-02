# Q205: depositETH Buffer Over Reservation Fee Mint rsETH P0205

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: rsETH transfer route; amount case 31.999999 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case 31.999999 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use single transaction to exercise the buffer over-reservation path against depositETH and look for fee mint breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: rsETH transfer route; amount case 31.999999 ether; timing same block before updateRSETHPrice; caller model EOA caller.
