# Q3135: getETHDistributionData Fee On Transfer Token Skew Price Update withdrawal P3135

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to failure to deliver promised returns without principal loss? Probe condition: withdrawal request nonce route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: a helper contract batching allowed public calls; probe condition: withdrawal request nonce route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the fee-on-transfer token skew path against getETHDistributionData and look for price update breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: withdrawal request nonce route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller.
