# Q249: depositETH Malformed Referral Payload Pause Race LRTUnstakingVault P0249

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and supply very large or unusual referralId data on hot user flows, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to temporary freezing of funds? Probe condition: LRTUnstakingVault instant-liquidity route; amount case 32.000001 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: supply very large or unusual referralId data on hot user flows; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: LRTUnstakingVault instant-liquidity route; amount case 32.000001 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the malformed referral payload path against depositETH and look for pause race breaking value conservation or liveness.
- Invariant to test: unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: LRTUnstakingVault instant-liquidity route; amount case 32.000001 ether; timing same block before updateRSETHPrice; caller model EOA caller.
