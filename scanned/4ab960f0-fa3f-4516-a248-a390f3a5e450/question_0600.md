# Q600: depositAsset Buffer Over Reservation Reentrancy Swell P0600

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to temporary freezing of funds? Probe condition: Swell swETH legacy route; amount case 1 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: attacker-created state followed by an honest operator action; probe condition: Swell swETH legacy route; amount case 1 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the buffer over-reservation path against depositAsset and look for reentrancy breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: Swell swETH legacy route; amount case 1 ether; timing same block after updateRSETHPrice; caller model EOA caller.
