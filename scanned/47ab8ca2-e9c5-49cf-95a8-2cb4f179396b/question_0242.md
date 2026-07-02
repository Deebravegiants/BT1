# Q242: depositETH Malformed Referral Payload Reentrancy stETH P0242

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and supply very large or unusual referralId data on hot user flows, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: stETH supported asset route; amount case 32.000001 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: supply very large or unusual referralId data on hot user flows; validation style: two transactions before and after updateRSETHPrice; probe condition: stETH supported asset route; amount case 32.000001 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the malformed referral payload path against depositETH and look for reentrancy breaking value conservation or liveness.
- Invariant to test: unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: stETH supported asset route; amount case 32.000001 ether; timing same block before updateRSETHPrice; caller model EOA caller.
