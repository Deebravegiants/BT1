# Q595: depositAsset Buffer Over Reservation Oracle withdrawal P0595

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to temporary freezing of funds? Probe condition: withdrawal request nonce route; amount case 1 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: an attacker contract as msg.sender or recipient; probe condition: withdrawal request nonce route; amount case 1 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the buffer over-reservation path against depositAsset and look for oracle breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: withdrawal request nonce route; amount case 1 ether; timing same block after updateRSETHPrice; caller model EOA caller.
