# Q3578: updateRSETHPrice Nonce Collision Attempt Fee Mint daily P3578

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to permanent freezing of unclaimed yield? Probe condition: daily fee mint limit route; amount case deposit limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: two transactions before and after updateRSETHPrice; probe condition: daily fee mint limit route; amount case deposit limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the nonce collision attempt path against updateRSETHPrice and look for fee mint breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: daily fee mint limit route; amount case deposit limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
