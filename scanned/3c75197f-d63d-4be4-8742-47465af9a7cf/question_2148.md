# Q2148: getRsETHAmountToMint Claim Replay Rounding LRTConverter P2148

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: LRTConverter ETH-in-withdrawal route; amount case 0.01 ether; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: attacker-created state followed by an honest operator action; probe condition: LRTConverter ETH-in-withdrawal route; amount case 0.01 ether; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the claim replay path against getRsETHAmountToMint and look for rounding breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: LRTConverter ETH-in-withdrawal route; amount case 0.01 ether; timing one second before daily reset; caller model EOA caller.
