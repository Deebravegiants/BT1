# Q3654: updateRSETHPrice Buffer Under Reservation Fee Mint deposit-limit P3654

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to direct theft of user funds? Probe condition: deposit-limit accounting route; amount case minAmount minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: compare many dust calls against one large call; probe condition: deposit-limit accounting route; amount case minAmount minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the buffer under-reservation path against updateRSETHPrice and look for fee mint breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: deposit-limit accounting route; amount case minAmount minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
