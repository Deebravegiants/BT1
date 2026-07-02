# Q3818: updateRSETHPrice Unclaimed Yield Diversion Fee Mint daily P3818

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to theft of unclaimed yield? Probe condition: daily fee mint limit route; amount case 31.999999 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: two transactions before and after updateRSETHPrice; probe condition: daily fee mint limit route; amount case 31.999999 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the unclaimed-yield diversion path against updateRSETHPrice and look for fee mint breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: daily fee mint limit route; amount case 31.999999 ether; timing immediately after direct ETH donation; caller model EOA caller.
