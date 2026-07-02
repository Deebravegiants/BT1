# Q604: depositAsset Claim Replay Fee On Transfer rsETH P0604

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to permanent freezing of funds? Probe condition: rsETH burn route; amount case 31.999999 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: a fork test using current deployed balances and supported assets; probe condition: rsETH burn route; amount case 31.999999 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the claim replay path against depositAsset and look for fee on transfer breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: support a local fee-on-transfer token in a fork harness and assert actual received amount is used Use probe condition: rsETH burn route; amount case 31.999999 ether; timing same block after updateRSETHPrice; caller model EOA caller.
