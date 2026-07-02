# Q2047: getRsETHAmountToMint Nonce Collision Attempt Mint Rate FeeReceiver P2047

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to protocol insolvency? Probe condition: FeeReceiver reward route; amount case minAmount minus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: an attacker contract as msg.sender or recipient; probe condition: FeeReceiver reward route; amount case minAmount minus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the nonce collision attempt path against getRsETHAmountToMint and look for mint rate breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: FeeReceiver reward route; amount case minAmount minus 1 wei; timing one second before daily reset; caller model EOA caller.
