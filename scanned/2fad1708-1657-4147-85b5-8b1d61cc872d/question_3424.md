# Q3424: getETHDistributionData Committed Assets Desync eth Accounting rsETH P3424

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: rsETH burn route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: a fork test using current deployed balances and supported assets; probe condition: rsETH burn route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the committed-assets desync path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: rsETH burn route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller.
