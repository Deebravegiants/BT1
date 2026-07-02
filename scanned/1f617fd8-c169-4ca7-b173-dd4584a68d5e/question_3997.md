# Q3997: getAssetPrice Highest Price Ratchet Zero Price daily P3997

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, zero price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to temporary freezing of funds? Probe condition: daily mint limit route; amount case deposit limit plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: one transaction using a contract wallet and controlled calldata; probe condition: daily mint limit route; amount case deposit limit plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use single transaction to exercise the highest-price ratchet path against getAssetPrice and look for zero price breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, zero price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: mock zero/near-zero oracle values and assert no division path creates free assets or permanent freezes Use probe condition: daily mint limit route; amount case deposit limit plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
