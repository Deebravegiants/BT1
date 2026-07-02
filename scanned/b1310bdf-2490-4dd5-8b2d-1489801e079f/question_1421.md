# Q1421: receiveFromLRTConverter Asset Identity Confusion Price Update ETH P1421

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to temporary freezing of funds? Probe condition: ETH sentinel route; amount case 32 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries; validation style: several attacker accounts creating adjacent requests; probe condition: ETH sentinel route; amount case 32 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the asset identity confusion path against receiveFromLRTConverter and look for price update breaking value conservation or liveness.
- Invariant to test: ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: ETH sentinel route; amount case 32 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
