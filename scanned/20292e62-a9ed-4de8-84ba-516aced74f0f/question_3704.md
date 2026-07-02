# Q3704: updateRSETHPrice Malformed Referral Payload Pause Race rsETH P3704

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and supply very large or unusual referralId data on hot user flows, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to failure to deliver promised returns without principal loss? Probe condition: rsETH burn route; amount case 1 gwei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: supply very large or unusual referralId data on hot user flows; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case 1 gwei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the malformed referral payload path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: rsETH burn route; amount case 1 gwei; timing immediately after direct ETH donation; caller model EOA caller.
