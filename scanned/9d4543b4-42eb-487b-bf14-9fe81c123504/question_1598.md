# Q1598: receiveFromNodeDelegator Fee On Transfer Token Skew Deposit Limit daily P1598

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: daily fee mint limit route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: two transactions before and after updateRSETHPrice; probe condition: daily fee mint limit route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the fee-on-transfer token skew path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: daily fee mint limit route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
