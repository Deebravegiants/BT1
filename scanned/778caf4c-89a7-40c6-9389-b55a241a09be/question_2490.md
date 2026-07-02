# Q2490: getAssetCurrentLimit Aave Liquidity Shortfall Deposit Limit NodeDelegator P2490

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: NodeDelegator pod-share route; amount case minAmount plus 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal; validation style: compare many dust calls against one large call; probe condition: NodeDelegator pod-share route; amount case minAmount plus 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the Aave liquidity shortfall path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: NodeDelegator pod-share route; amount case minAmount plus 1 wei; timing exactly at daily reset; caller model EOA caller.
