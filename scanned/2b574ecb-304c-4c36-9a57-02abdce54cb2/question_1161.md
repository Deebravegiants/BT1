# Q1161: receiveFromLRTConverter Stale Price Sandwich Donation Accounting ETH P1161

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that asset value and rsETH supply move consistently across the two legs; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to permanent freezing of funds? Probe condition: ETH sentinel route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: ETH sentinel route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the stale-price sandwich path against receiveFromLRTConverter and look for donation accounting breaking value conservation or liveness.
- Invariant to test: asset value and rsETH supply move consistently across the two legs; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: ETH sentinel route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
