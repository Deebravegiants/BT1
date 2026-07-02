# Q1446: receiveFromLRTConverter Allowance Race Converter Desync LRTOracle P1446

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to protocol insolvency? Probe condition: LRTOracle price route; amount case 32.000001 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: compare many dust calls against one large call; probe condition: LRTOracle price route; amount case 32.000001 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the allowance race path against receiveFromLRTConverter and look for converter desync breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: LRTOracle price route; amount case 32.000001 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
