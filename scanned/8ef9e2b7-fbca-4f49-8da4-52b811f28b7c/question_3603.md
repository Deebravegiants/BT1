# Q3603: updateRSETHPrice Oracle Decimal Mismatch Rounding ETHx P3603

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to direct theft of user funds? Probe condition: ETHx supported asset route; amount case 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: a helper contract batching allowed public calls; probe condition: ETHx supported asset route; amount case 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the oracle decimal mismatch path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: ETHx supported asset route; amount case 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
