# Q55: depositETH Direct ETH Donation Skew Pause Race withdrawal P0055

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to direct theft of user funds? Probe condition: withdrawal request nonce route; amount case minAmount minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: an attacker contract as msg.sender or recipient; probe condition: withdrawal request nonce route; amount case minAmount minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the direct ETH donation skew path against depositETH and look for pause race breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: withdrawal request nonce route; amount case minAmount minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
