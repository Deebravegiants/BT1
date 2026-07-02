# Q1992: getRsETHAmountToMint Fee On Transfer Token Skew Mint Rate Aave P1992

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to protocol insolvency? Probe condition: Aave aWETH liquidity route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: attacker-created state followed by an honest operator action; probe condition: Aave aWETH liquidity route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the fee-on-transfer token skew path against getRsETHAmountToMint and look for mint rate breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: Aave aWETH liquidity route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
