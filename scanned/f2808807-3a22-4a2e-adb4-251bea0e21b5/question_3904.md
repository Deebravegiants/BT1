# Q3904: getAssetPrice Fee On Transfer Token Skew Zero Price rsETH P3904

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, zero price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to temporary freezing of funds? Probe condition: rsETH burn route; amount case available liquidity minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: a fork test using current deployed balances and supported assets; probe condition: rsETH burn route; amount case available liquidity minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the fee-on-transfer token skew path against getAssetPrice and look for zero price breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, zero price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: mock zero/near-zero oracle values and assert no division path creates free assets or permanent freezes Use probe condition: rsETH burn route; amount case available liquidity minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
