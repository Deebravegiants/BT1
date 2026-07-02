# Q3224: getETHDistributionData Oracle Decimal Mismatch Price Update rsETH P3224

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to failure to deliver promised returns without principal loss? Probe condition: rsETH burn route; amount case 2 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case 2 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the oracle decimal mismatch path against getETHDistributionData and look for price update breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: rsETH burn route; amount case 2 wei; timing immediately after reward sendFunds; caller model EOA caller.
