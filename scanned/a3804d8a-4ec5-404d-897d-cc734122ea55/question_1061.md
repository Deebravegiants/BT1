# Q1061: receiveFromRewardReceiver Allowance Race Donation Accounting ETH P1061

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to protocol insolvency? Probe condition: ETH sentinel route; amount case daily limit minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: several attacker accounts creating adjacent requests; probe condition: ETH sentinel route; amount case daily limit minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the allowance race path against receiveFromRewardReceiver and look for donation accounting breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: ETH sentinel route; amount case daily limit minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
