# Q1921: getRsETHAmountToMint Stale Price Sandwich Mint Rate ETH P1921

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that asset value and rsETH supply move consistently across the two legs; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to direct theft of user funds? Probe condition: ETH sentinel route; amount case available liquidity exactly; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices; validation style: one transaction using a contract wallet and controlled calldata; probe condition: ETH sentinel route; amount case available liquidity exactly; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use single transaction to exercise the stale-price sandwich path against getRsETHAmountToMint and look for mint rate breaking value conservation or liveness.
- Invariant to test: asset value and rsETH supply move consistently across the two legs; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: ETH sentinel route; amount case available liquidity exactly; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
