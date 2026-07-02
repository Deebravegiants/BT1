# Q516: depositAsset Nonce Collision Attempt Fee On Transfer queued P0516

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to permanent freezing of funds? Probe condition: queued buffer route; amount case 1 gwei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: attacker-created state followed by an honest operator action; probe condition: queued buffer route; amount case 1 gwei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the nonce collision attempt path against depositAsset and look for fee on transfer breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: support a local fee-on-transfer token in a fork harness and assert actual received amount is used Use probe condition: queued buffer route; amount case 1 gwei; timing same block after updateRSETHPrice; caller model EOA caller.
