# Q1379: receiveFromLRTConverter Claim Replay Donation Accounting Lido P1379

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to permanent freezing of funds? Probe condition: Lido stETH unstake route; amount case 0.1 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case 0.1 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the claim replay path against receiveFromLRTConverter and look for donation accounting breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: Lido stETH unstake route; amount case 0.1 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
