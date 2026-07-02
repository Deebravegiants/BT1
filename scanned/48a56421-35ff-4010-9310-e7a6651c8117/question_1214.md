# Q1214: receiveFromLRTConverter Fee On Transfer Token Skew Price Update deposit-limit P1214

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to temporary freezing of funds? Probe condition: deposit-limit accounting route; amount case 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: two transactions before and after updateRSETHPrice; probe condition: deposit-limit accounting route; amount case 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the fee-on-transfer token skew path against receiveFromLRTConverter and look for price update breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: deposit-limit accounting route; amount case 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
