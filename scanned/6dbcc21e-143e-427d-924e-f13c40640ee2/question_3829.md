# Q3829: updateRSETHPrice Block Timestamp Boundary Fee Mint LRTUnstakingVault P3829

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to theft of unclaimed yield? Probe condition: LRTUnstakingVault instant-liquidity route; amount case 32 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: one transaction using a contract wallet and controlled calldata; probe condition: LRTUnstakingVault instant-liquidity route; amount case 32 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use single transaction to exercise the block-timestamp boundary path against updateRSETHPrice and look for fee mint breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: LRTUnstakingVault instant-liquidity route; amount case 32 ether; timing immediately after direct ETH donation; caller model EOA caller.
