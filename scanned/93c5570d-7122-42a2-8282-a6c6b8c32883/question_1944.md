# Q1944: getRsETHAmountToMint Round Down Accumulation Mint Rate rsETH P1944

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to direct theft of user funds? Probe condition: rsETH burn route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: attacker-created state followed by an honest operator action; probe condition: rsETH burn route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the round-down accumulation path against getRsETHAmountToMint and look for mint rate breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: rsETH burn route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
