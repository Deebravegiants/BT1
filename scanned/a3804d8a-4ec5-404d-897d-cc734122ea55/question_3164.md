# Q3164: getETHDistributionData Reentrant Token Callback Converter Desync rsETH P3164

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to temporary freezing of funds? Probe condition: rsETH burn route; amount case deposit limit minus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case deposit limit minus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the reentrant token callback path against getETHDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: rsETH burn route; amount case deposit limit minus 1 wei; timing one second after daily reset; caller model EOA caller.
