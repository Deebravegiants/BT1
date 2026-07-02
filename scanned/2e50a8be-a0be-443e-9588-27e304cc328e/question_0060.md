# Q60: depositETH Direct ETH Donation Skew Reentrancy Swell P0060

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to direct theft of user funds? Probe condition: Swell swETH legacy route; amount case minAmount minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: attacker-created state followed by an honest operator action; probe condition: Swell swETH legacy route; amount case minAmount minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the direct ETH donation skew path against depositETH and look for reentrancy breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: Swell swETH legacy route; amount case minAmount minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
