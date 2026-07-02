# Q540: depositAsset Oracle Decimal Mismatch Oracle Swell P0540

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to temporary freezing of funds? Probe condition: Swell swETH legacy route; amount case 0.001 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: attacker-created state followed by an honest operator action; probe condition: Swell swETH legacy route; amount case 0.001 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the oracle decimal mismatch path against depositAsset and look for oracle breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: Swell swETH legacy route; amount case 0.001 ether; timing same block after updateRSETHPrice; caller model EOA caller.
