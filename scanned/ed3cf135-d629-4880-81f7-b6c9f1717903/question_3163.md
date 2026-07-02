# Q3163: getETHDistributionData Reentrant Token Callback Donation Accounting ETHx P3163

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to protocol insolvency? Probe condition: ETHx supported asset route; amount case deposit limit minus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path; validation style: an attacker contract as msg.sender or recipient; probe condition: ETHx supported asset route; amount case deposit limit minus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the reentrant token callback path against getETHDistributionData and look for donation accounting breaking value conservation or liveness.
- Invariant to test: nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: ETHx supported asset route; amount case deposit limit minus 1 wei; timing one second after daily reset; caller model EOA caller.
