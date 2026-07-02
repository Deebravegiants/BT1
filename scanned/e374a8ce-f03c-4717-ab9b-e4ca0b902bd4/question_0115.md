# Q115: depositETH Queue Head Blocking Reentrancy withdrawal P0115

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and place a pathological first queue item that blocks later honest requests from completing, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that one request cannot permanently or temporarily freeze unrelated user funds; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to direct theft of user funds? Probe condition: withdrawal request nonce route; amount case 1 gwei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: place a pathological first queue item that blocks later honest requests from completing; validation style: an attacker contract as msg.sender or recipient; probe condition: withdrawal request nonce route; amount case 1 gwei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the queue head blocking path against depositETH and look for reentrancy breaking value conservation or liveness.
- Invariant to test: one request cannot permanently or temporarily freeze unrelated user funds; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: withdrawal request nonce route; amount case 1 gwei; timing same block before updateRSETHPrice; caller model EOA caller.
