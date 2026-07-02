# Q913: receiveFromRewardReceiver Oracle Decimal Mismatch Donation Accounting Merkle-free P0913

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to protocol insolvency? Probe condition: Merkle-free yield accounting route; amount case 1 gwei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: one transaction using a contract wallet and controlled calldata; probe condition: Merkle-free yield accounting route; amount case 1 gwei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use single transaction to exercise the oracle decimal mismatch path against receiveFromRewardReceiver and look for donation accounting breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: Merkle-free yield accounting route; amount case 1 gwei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
