# Q895: receiveFromRewardReceiver Nonce Collision Attempt Donation Accounting withdrawal P0895

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to protocol insolvency? Probe condition: withdrawal request nonce route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: an attacker contract as msg.sender or recipient; probe condition: withdrawal request nonce route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the nonce collision attempt path against receiveFromRewardReceiver and look for donation accounting breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: withdrawal request nonce route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
