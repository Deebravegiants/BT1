# Q257: depositETH Gas Amplified Loop Deposit Limit daily P0257

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and grow a user-controlled queue/list then trigger a function that iterates it in a critical flow, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that user-controlled growth remains bounded and cannot cause unbounded gas consumption; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to direct theft of user funds? Probe condition: daily mint limit route; amount case 32.000001 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: grow a user-controlled queue/list then trigger a function that iterates it in a critical flow; validation style: several attacker accounts creating adjacent requests; probe condition: daily mint limit route; amount case 32.000001 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the gas-amplified loop path against depositETH and look for deposit limit breaking value conservation or liveness.
- Invariant to test: user-controlled growth remains bounded and cannot cause unbounded gas consumption; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: daily mint limit route; amount case 32.000001 ether; timing same block before updateRSETHPrice; caller model EOA caller.
