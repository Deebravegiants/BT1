# Q3507: updateRSETHPrice Direct ETH Donation Skew Fee Mint FeeReceiver P3507

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to failure to deliver promised returns without principal loss? Probe condition: FeeReceiver reward route; amount case available liquidity minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: a helper contract batching allowed public calls; probe condition: FeeReceiver reward route; amount case available liquidity minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the direct ETH donation skew path against updateRSETHPrice and look for fee mint breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: FeeReceiver reward route; amount case available liquidity minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
