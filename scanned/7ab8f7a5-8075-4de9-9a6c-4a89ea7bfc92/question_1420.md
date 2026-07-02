# Q1420: receiveFromLRTConverter Asset Identity Confusion Converter Desync Swell P1420

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to protocol insolvency? Probe condition: Swell swETH legacy route; amount case 31.999999 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries; validation style: a fork test using current deployed balances and supported assets; probe condition: Swell swETH legacy route; amount case 31.999999 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the asset identity confusion path against receiveFromLRTConverter and look for converter desync breaking value conservation or liveness.
- Invariant to test: ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: Swell swETH legacy route; amount case 31.999999 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
