# Q1740: receiveFromNodeDelegator Buffer Under Reservation Withdrawal Liquidity Swell P1740

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to failure to deliver promised returns without principal loss? Probe condition: Swell swETH legacy route; amount case 0.001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: attacker-created state followed by an honest operator action; probe condition: Swell swETH legacy route; amount case 0.001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the buffer under-reservation path against receiveFromNodeDelegator and look for withdrawal liquidity breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: assert user-created demand cannot strand unrelated users by consuming liquidity accounting Use probe condition: Swell swETH legacy route; amount case 0.001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
