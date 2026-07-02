# Q840: receiveFromRewardReceiver Fee On Transfer Token Skew Donation Accounting Swell P0840

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to protocol insolvency? Probe condition: Swell swETH legacy route; amount case 2 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: attacker-created state followed by an honest operator action; probe condition: Swell swETH legacy route; amount case 2 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the fee-on-transfer token skew path against receiveFromRewardReceiver and look for donation accounting breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: Swell swETH legacy route; amount case 2 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
