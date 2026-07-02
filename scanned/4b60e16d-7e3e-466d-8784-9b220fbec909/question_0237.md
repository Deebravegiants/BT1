# Q237: depositETH Failed External Call Ordering Reentrancy daily P0237

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and force an external transfer/withdraw/deposit call to fail after local accounting mutates, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: daily mint limit route; amount case 32 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: force an external transfer/withdraw/deposit call to fail after local accounting mutates; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: daily mint limit route; amount case 32 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the failed external call ordering path against depositETH and look for reentrancy breaking value conservation or liveness.
- Invariant to test: failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: daily mint limit route; amount case 32 ether; timing same block before updateRSETHPrice; caller model EOA caller.
