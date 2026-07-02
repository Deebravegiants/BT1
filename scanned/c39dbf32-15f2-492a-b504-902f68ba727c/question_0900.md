# Q900: receiveFromRewardReceiver Nonce Collision Attempt Fee Mint Swell P0900

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to theft of unclaimed yield? Probe condition: Swell swETH legacy route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: attacker-created state followed by an honest operator action; probe condition: Swell swETH legacy route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the nonce collision attempt path against receiveFromRewardReceiver and look for fee mint breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: Swell swETH legacy route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
