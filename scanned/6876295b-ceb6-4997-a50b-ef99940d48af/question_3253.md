# Q3253: getETHDistributionData Aave Liquidity Shortfall Price Update Merkle-free P3253

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to failure to deliver promised returns without principal loss? Probe condition: Merkle-free yield accounting route; amount case minAmount minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal; validation style: one transaction using a contract wallet and controlled calldata; probe condition: Merkle-free yield accounting route; amount case minAmount minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use single transaction to exercise the Aave liquidity shortfall path against getETHDistributionData and look for price update breaking value conservation or liveness.
- Invariant to test: external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Merkle-free yield accounting route; amount case minAmount minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
