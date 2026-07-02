# Q911: receiveFromRewardReceiver FirstExcludedIndex Boundary Fee Mint EigenLayer P0911

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to theft of unclaimed yield? Probe condition: EigenLayer queued-withdrawal route; amount case 1 gwei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: a local supported-token harness with configurable transfer behavior; probe condition: EigenLayer queued-withdrawal route; amount case 1 gwei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the firstExcludedIndex boundary path against receiveFromRewardReceiver and look for fee mint breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: EigenLayer queued-withdrawal route; amount case 1 gwei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
