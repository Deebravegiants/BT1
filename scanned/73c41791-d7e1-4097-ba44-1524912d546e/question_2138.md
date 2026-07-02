# Q2138: getRsETHAmountToMint Claim Replay Stale Price daily P2138

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to protocol insolvency? Probe condition: daily fee mint limit route; amount case 0.001 ether; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: two transactions before and after updateRSETHPrice; probe condition: daily fee mint limit route; amount case 0.001 ether; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the claim replay path against getRsETHAmountToMint and look for stale price breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: sequence price update/deposit/withdraw with stale and fresh prices and assert no profitable round trip. Use probe condition: daily fee mint limit route; amount case 0.001 ether; timing one second before daily reset; caller model EOA caller.
