# Q439: depositAsset Direct ETH Donation Skew Reentrancy Lido P0439

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to direct theft of user funds? Probe condition: Lido stETH unstake route; amount case 2 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: an attacker contract as msg.sender or recipient; probe condition: Lido stETH unstake route; amount case 2 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the direct ETH donation skew path against depositAsset and look for reentrancy breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: Lido stETH unstake route; amount case 2 wei; timing same block after updateRSETHPrice; caller model EOA caller.
