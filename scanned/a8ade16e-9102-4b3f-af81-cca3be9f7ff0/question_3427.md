# Q3427: getETHDistributionData Committed Assets Desync Price Update FeeReceiver P3427

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to failure to deliver promised returns without principal loss? Probe condition: FeeReceiver reward route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: an attacker contract as msg.sender or recipient; probe condition: FeeReceiver reward route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the committed-assets desync path against getETHDistributionData and look for price update breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: FeeReceiver reward route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller.
