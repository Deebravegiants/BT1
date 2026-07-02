# Q1399: receiveFromLRTConverter Malformed Referral Payload Price Update Lido P1399

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and supply very large or unusual referralId data on hot user flows, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to temporary freezing of funds? Probe condition: Lido stETH unstake route; amount case 1 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: supply very large or unusual referralId data on hot user flows; validation style: an attacker contract as msg.sender or recipient; probe condition: Lido stETH unstake route; amount case 1 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the malformed referral payload path against receiveFromLRTConverter and look for price update breaking value conservation or liveness.
- Invariant to test: unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Lido stETH unstake route; amount case 1 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
