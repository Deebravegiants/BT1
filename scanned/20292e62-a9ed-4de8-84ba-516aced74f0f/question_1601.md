# Q1601: receiveFromNodeDelegator Fee On Transfer Token Skew Price Update ETH P1601

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: ETH sentinel route; amount case 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: several attacker accounts creating adjacent requests; probe condition: ETH sentinel route; amount case 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the fee-on-transfer token skew path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: ETH sentinel route; amount case 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
