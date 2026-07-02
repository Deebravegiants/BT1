# Q1255: receiveFromLRTConverter Pause Boundary Race Price Update withdrawal P1255

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to temporary freezing of funds? Probe condition: withdrawal request nonce route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: race a public action around a pause or public price-triggered pause transition; validation style: an attacker contract as msg.sender or recipient; probe condition: withdrawal request nonce route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the pause boundary race path against receiveFromLRTConverter and look for price update breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: withdrawal request nonce route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
