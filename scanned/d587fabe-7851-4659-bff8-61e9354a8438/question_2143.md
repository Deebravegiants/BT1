# Q2143: getRsETHAmountToMint Claim Replay Mint Rate ETHx P2143

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to direct theft of user funds? Probe condition: ETHx supported asset route; amount case 0.01 ether; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: an attacker contract as msg.sender or recipient; probe condition: ETHx supported asset route; amount case 0.01 ether; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the claim replay path against getRsETHAmountToMint and look for mint rate breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: ETHx supported asset route; amount case 0.01 ether; timing one second before daily reset; caller model EOA caller.
