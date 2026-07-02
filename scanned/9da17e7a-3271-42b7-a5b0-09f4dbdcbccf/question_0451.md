# Q451: depositAsset Fee On Transfer Token Skew Oracle EigenLayer P0451

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to permanent freezing of funds? Probe condition: EigenLayer queued-withdrawal route; amount case minAmount minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: an attacker contract as msg.sender or recipient; probe condition: EigenLayer queued-withdrawal route; amount case minAmount minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the fee-on-transfer token skew path against depositAsset and look for oracle breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: EigenLayer queued-withdrawal route; amount case minAmount minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
