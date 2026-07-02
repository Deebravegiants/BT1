# Q3147: getETHDistributionData Rebasing Balance Drift eth Accounting FeeReceiver P3147

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and let a supported rebasing LST balance change between request creation and final settlement, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: FeeReceiver reward route; amount case available liquidity plus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: let a supported rebasing LST balance change between request creation and final settlement; validation style: a helper contract batching allowed public calls; probe condition: FeeReceiver reward route; amount case available liquidity plus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the rebasing balance drift path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: FeeReceiver reward route; amount case available liquidity plus 1 wei; timing one second after daily reset; caller model EOA caller.
