# Q1517: receiveFromLRTConverter Unclaimed Yield Diversion Price Update daily P1517

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to temporary freezing of funds? Probe condition: daily mint limit route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: several attacker accounts creating adjacent requests; probe condition: daily mint limit route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the unclaimed-yield diversion path against receiveFromLRTConverter and look for price update breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: daily mint limit route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
