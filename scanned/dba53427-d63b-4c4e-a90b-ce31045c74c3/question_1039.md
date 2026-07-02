# Q1039: receiveFromRewardReceiver Asset Identity Confusion Donation Accounting Lido P1039

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to protocol insolvency? Probe condition: Lido stETH unstake route; amount case 32 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries; validation style: an attacker contract as msg.sender or recipient; probe condition: Lido stETH unstake route; amount case 32 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the asset identity confusion path against receiveFromRewardReceiver and look for donation accounting breaking value conservation or liveness.
- Invariant to test: ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: Lido stETH unstake route; amount case 32 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
