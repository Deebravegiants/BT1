# Q247: depositETH Malformed Referral Payload Rounding FeeReceiver P0247

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and supply very large or unusual referralId data on hot user flows, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: FeeReceiver reward route; amount case 32.000001 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: supply very large or unusual referralId data on hot user flows; validation style: an attacker contract as msg.sender or recipient; probe condition: FeeReceiver reward route; amount case 32.000001 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the malformed referral payload path against depositETH and look for rounding breaking value conservation or liveness.
- Invariant to test: unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: FeeReceiver reward route; amount case 32.000001 ether; timing same block before updateRSETHPrice; caller model EOA caller.
