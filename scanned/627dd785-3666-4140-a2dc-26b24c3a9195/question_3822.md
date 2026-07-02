# Q3822: updateRSETHPrice Unclaimed Yield Diversion Price Update stETH P3822

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to direct theft of user funds? Probe condition: stETH supported asset route; amount case 32 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: compare many dust calls against one large call; probe condition: stETH supported asset route; amount case 32 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the unclaimed-yield diversion path against updateRSETHPrice and look for price update breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: stETH supported asset route; amount case 32 ether; timing immediately after direct ETH donation; caller model EOA caller.
