# Q3895: getAssetPrice Direct ETH Donation Skew Oracle withdrawal P3895

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to direct theft of user funds? Probe condition: withdrawal request nonce route; amount case daily limit exactly; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: an attacker contract as msg.sender or recipient; probe condition: withdrawal request nonce route; amount case daily limit exactly; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the direct ETH donation skew path against getAssetPrice and look for oracle breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: withdrawal request nonce route; amount case daily limit exactly; timing immediately after direct ETH donation; caller model EOA caller.
