# Q510: depositAsset Nonce Collision Attempt Fee On Transfer NodeDelegator P0510

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to direct theft of user funds? Probe condition: NodeDelegator pod-share route; amount case 1 gwei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: compare many dust calls against one large call; probe condition: NodeDelegator pod-share route; amount case 1 gwei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the nonce collision attempt path against depositAsset and look for fee on transfer breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: support a local fee-on-transfer token in a fork harness and assert actual received amount is used Use probe condition: NodeDelegator pod-share route; amount case 1 gwei; timing same block after updateRSETHPrice; caller model EOA caller.
