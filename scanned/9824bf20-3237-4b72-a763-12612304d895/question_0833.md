# Q833: receiveFromRewardReceiver Fee On Transfer Token Skew Fee Mint Merkle-free P0833

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to theft of unclaimed yield? Probe condition: Merkle-free yield accounting route; amount case 2 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: several attacker accounts creating adjacent requests; probe condition: Merkle-free yield accounting route; amount case 2 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the fee-on-transfer token skew path against receiveFromRewardReceiver and look for fee mint breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: Merkle-free yield accounting route; amount case 2 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
