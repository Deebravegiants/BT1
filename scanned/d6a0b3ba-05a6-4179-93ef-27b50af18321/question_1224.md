# Q1224: receiveFromLRTConverter Fee On Transfer Token Skew Donation Accounting rsETH P1224

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to permanent freezing of funds? Probe condition: rsETH burn route; amount case 2 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: attacker-created state followed by an honest operator action; probe condition: rsETH burn route; amount case 2 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the fee-on-transfer token skew path against receiveFromLRTConverter and look for donation accounting breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: rsETH burn route; amount case 2 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
