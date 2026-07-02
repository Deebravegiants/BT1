# Q544: depositAsset Highest Price Ratchet Reentrancy rsETH P0544

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to permanent freezing of funds? Probe condition: rsETH burn route; amount case 0.01 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: a fork test using current deployed balances and supported assets; probe condition: rsETH burn route; amount case 0.01 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the highest-price ratchet path against depositAsset and look for reentrancy breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: rsETH burn route; amount case 0.01 ether; timing same block after updateRSETHPrice; caller model EOA caller.
