# Q3839: updateRSETHPrice Block Timestamp Boundary Fee Mint Lido P3839

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to failure to deliver promised returns without principal loss? Probe condition: Lido stETH unstake route; amount case 32 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case 32 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the block-timestamp boundary path against updateRSETHPrice and look for fee mint breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: Lido stETH unstake route; amount case 32 ether; timing immediately after direct ETH donation; caller model EOA caller.
