# Q2140: getRsETHAmountToMint Claim Replay Rounding Swell P2140

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to direct theft of user funds? Probe condition: Swell swETH legacy route; amount case 0.001 ether; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: a fork test using current deployed balances and supported assets; probe condition: Swell swETH legacy route; amount case 0.001 ether; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the claim replay path against getRsETHAmountToMint and look for rounding breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: Swell swETH legacy route; amount case 0.001 ether; timing one second before daily reset; caller model EOA caller.
