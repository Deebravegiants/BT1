# Q606: depositAsset Claim Replay Oracle LRTOracle P0606

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to temporary freezing of funds? Probe condition: LRTOracle price route; amount case 31.999999 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: compare many dust calls against one large call; probe condition: LRTOracle price route; amount case 31.999999 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the claim replay path against depositAsset and look for oracle breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: LRTOracle price route; amount case 31.999999 ether; timing same block after updateRSETHPrice; caller model EOA caller.
