# Q632: depositAsset Malformed Referral Payload Fee On Transfer Aave P0632

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and supply very large or unusual referralId data on hot user flows, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to protocol insolvency? Probe condition: Aave aWETH liquidity route; amount case 32 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: supply very large or unusual referralId data on hot user flows; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: Aave aWETH liquidity route; amount case 32 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the malformed referral payload path against depositAsset and look for fee on transfer breaking value conservation or liveness.
- Invariant to test: unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: support a local fee-on-transfer token in a fork harness and assert actual received amount is used Use probe condition: Aave aWETH liquidity route; amount case 32 ether; timing same block after updateRSETHPrice; caller model EOA caller.
