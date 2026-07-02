# Q1704: receiveFromNodeDelegator Highest Price Ratchet Donation Accounting rsETH P1704

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to permanent freezing of funds? Probe condition: rsETH burn route; amount case 1 gwei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: attacker-created state followed by an honest operator action; probe condition: rsETH burn route; amount case 1 gwei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the highest-price ratchet path against receiveFromNodeDelegator and look for donation accounting breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: rsETH burn route; amount case 1 gwei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
