# Q83: depositETH Rebasing Balance Drift Pause Race ETHx P0083

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and let a supported rebasing LST balance change between request creation and final settlement, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: ETHx supported asset route; amount case minAmount plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: let a supported rebasing LST balance change between request creation and final settlement; validation style: a local supported-token harness with configurable transfer behavior; probe condition: ETHx supported asset route; amount case minAmount plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the rebasing balance drift path against depositETH and look for pause race breaking value conservation or liveness.
- Invariant to test: rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: ETHx supported asset route; amount case minAmount plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
