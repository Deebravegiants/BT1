# Q2010: getRsETHAmountToMint Reentrant Token Callback Mint Rate NodeDelegator P2010

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to direct theft of user funds? Probe condition: NodeDelegator pod-share route; amount case 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path; validation style: compare many dust calls against one large call; probe condition: NodeDelegator pod-share route; amount case 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the reentrant token callback path against getRsETHAmountToMint and look for mint rate breaking value conservation or liveness.
- Invariant to test: nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: NodeDelegator pod-share route; amount case 1 wei; timing one second before daily reset; caller model EOA caller.
