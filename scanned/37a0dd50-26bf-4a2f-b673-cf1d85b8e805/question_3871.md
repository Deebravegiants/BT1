# Q3871: getAssetPrice Round Up Insolvency Zero Price EigenLayer P3871

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, zero price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to temporary freezing of funds? Probe condition: EigenLayer queued-withdrawal route; amount case daily limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: an attacker contract as msg.sender or recipient; probe condition: EigenLayer queued-withdrawal route; amount case daily limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the round-up insolvency path against getAssetPrice and look for zero price breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, zero price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: mock zero/near-zero oracle values and assert no division path creates free assets or permanent freezes Use probe condition: EigenLayer queued-withdrawal route; amount case daily limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
